from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List, Optional
from common.database import get_session
from cou_course.models.lesson import Lesson
from cou_course.models.quiz import Quiz
from cou_course.models.question import Question
from cou_course.models.flashcard import Flashcard
from cou_course.models.mindmap import Mindmap
from cou_course.models.memory_game import MemoryGame
from cou_course.models.memory_game_pair import MemoryGamePair
from cou_course.models.topic import Topic
from cou_course.models.course_learning import VideoListResponse, VideoInfo
from cou_course.schemas.lesson_schema import LessonCreate, LessonRead, LessonUpdate, LessonWithCourseInfo
from cou_course.schemas.quiz_schema import QuizCreate, QuizRead, QuizUpdate
from cou_course.schemas.question_schema import QuestionCreate, QuestionRead, QuestionUpdate
from cou_course.schemas.flashcard_schema import FlashcardCreate, FlashcardRead, FlashcardUpdate
from cou_course.schemas.mindmap_schema import MindmapCreate, MindmapRead, MindmapUpdate
from cou_course.schemas.memory_game_schema import MemoryGameCreate, MemoryGameRead, MemoryGameUpdate
from cou_course.schemas.topic_schema import TopicCreate, TopicRead, TopicUpdate
from cou_course.repositories.lesson_repository import LessonRepository
from cou_course.repositories.quiz_repository import QuizRepository
from cou_course.repositories.question_repository import QuestionRepository
from cou_course.repositories.flashcard_repository import FlashcardRepository
from cou_course.repositories.mindmap_repository import MindmapRepository
from cou_course.repositories.memory_game_repository import MemoryGameRepository
from cou_course.repositories.topic_repository import TopicRepository

# Azure Blob Storage imports
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/course-learning",
    tags=["Course Learning"]
)

# Azure Blob Storage setup
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if not AZURE_CONNECTION_STRING:
    raise ValueError("AZURE_STORAGE_CONNECTION_STRING environment variable is not set")

CONTAINER_NAME = "lessons"  # You can change this to your preferred container name

try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    # Get the container client
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    # Verify container exists
    if not container_client.exists():
        raise ValueError(f"Container '{CONTAINER_NAME}' does not exist in Azure Storage")
except Exception as e:
    raise ValueError(f"Failed to initialize Azure Blob Service Client: {str(e)}")

# ==================== VIDEO URL APIs ====================

@router.get("/videos/", response_model=VideoListResponse)
def fetch_videos():
    """Get all videos from Azure Blob Storage"""
    try:
        video_list = []
        
        # List all blobs in the container
        blob_list = container_client.list_blobs()
        
        for blob in blob_list:
            # Generate a URL for each blob
            video_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{blob.name}"
            video_info = VideoInfo(
                name=blob.name,
                url=video_url,
                content_type=blob.content_settings.content_type,
                size=blob.size
            )
            video_list.append(video_info)

        return VideoListResponse(videos=video_list)
    except Exception as e:
        logger.error(f"Failed to fetch videos: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch videos: {str(e)}")

@router.get("/videos/{video_path:path}", response_model=VideoInfo)
def get_video_by_path(video_path: str):
    """Get a specific video by its path/filename from Azure Blob Storage"""
    try:
        # Get the blob client for the specific video
        blob_client = container_client.get_blob_client(video_path)
        
        # Check if blob exists
        if not blob_client.exists():
            raise HTTPException(status_code=404, detail=f"Video '{video_path}' not found")
        
        # Get blob properties
        blob_properties = blob_client.get_blob_properties()
        
        # Generate URL
        video_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{video_path}"
        
        video_info = VideoInfo(
            name=video_path,
            url=video_url,
            content_type=blob_properties.content_settings.content_type,
            size=blob_properties.size
        )
        
        return video_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video '{video_path}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get video: {str(e)}")

@router.get("/hls/{lesson_folder}/master.m3u8", response_model=VideoInfo)
def get_hls_master_playlist(lesson_folder: str):
    """Get the master.m3u8 file for a specific lesson folder - for HLS player"""
    try:
        # Construct the path to master.m3u8 in the lesson folder
        master_playlist_path = f"{lesson_folder}/master.m3u8"
        
        # Get the blob client for the master playlist
        blob_client = container_client.get_blob_client(master_playlist_path)
        
        # Check if blob exists
        if not blob_client.exists():
            raise HTTPException(status_code=404, detail=f"Master playlist not found for lesson '{lesson_folder}'")
        
        # Get blob properties
        blob_properties = blob_client.get_blob_properties()
        
        # Generate URL for HLS player
        master_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{master_playlist_path}"
        
        video_info = VideoInfo(
            name=f"{lesson_folder}/master.m3u8",
            url=master_url,
            content_type=blob_properties.content_settings.content_type,
            size=blob_properties.size
        )
        
        return video_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get HLS master playlist for '{lesson_folder}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get HLS master playlist: {str(e)}")

@router.get("/hls/lessons/", response_model=dict)
def get_all_hls_lessons():
    """Get all lesson folders that contain HLS videos"""
    try:
        lesson_folders = set()
        
        # List all blobs in the container
        blob_list = container_client.list_blobs()
        
        for blob in blob_list:
            # Extract lesson folder name from blob path
            if "/" in blob.name:
                lesson_folder = blob.name.split("/")[0]
                lesson_folders.add(lesson_folder)
        
        # Get master playlist URLs for each lesson
        lessons_info = []
        for folder in sorted(lesson_folders):
            master_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{folder}/master.m3u8"
            lessons_info.append({
                "lesson_folder": folder,
                "master_playlist_url": master_url,
                "hls_player_url": master_url  # Direct URL for HLS player
            })

        return {
            "lessons": lessons_info,
            "total_lessons": len(lessons_info)
        }
    except Exception as e:
        logger.error(f"Failed to get all HLS lessons: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get HLS lessons: {str(e)}")

# ==================== LESSON APIs ====================

@router.post("/lessons/", response_model=LessonRead)
def create_lesson(lesson: LessonCreate, session: Session = Depends(get_session)):
    """Create a new lesson for a course"""
    return LessonRepository.create_lesson(session, lesson)

@router.get("/lessons/{lesson_id}", response_model=LessonRead)
def get_lesson(lesson_id: int, session: Session = Depends(get_session)):
    """Get a specific lesson by ID"""
    lesson = LessonRepository.get_lesson_by_id(session, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson

@router.get("/courses/{course_id}/lessons/", response_model=List[LessonWithCourseInfo])
def get_course_lessons(course_id: int, session: Session = Depends(get_session)):
    """Get all lessons for a specific course with course information"""
    try:
        # Get lessons for the course
        lessons = LessonRepository.get_lessons_by_course(session, course_id)
        
        # Enhance lessons with course information
        enhanced_lessons = []
        for lesson in lessons:
            lesson_dict = lesson.dict()
            # Map the lesson fields directly, including code and code_language
            lesson_dict.update({
                "course_code": lesson.code,  # Use lesson.code directly
                "course_code_language": lesson.code_language  # Use lesson.code_language directly
            })
            enhanced_lessons.append(LessonWithCourseInfo(**lesson_dict))
        
        return enhanced_lessons
    except Exception as e:
        logger.error(f"Failed to get lessons for course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get lessons: {str(e)}")

@router.put("/lessons/{lesson_id}", response_model=LessonRead)
def update_lesson(lesson_id: int, lesson_update: LessonUpdate, session: Session = Depends(get_session)):
    """Update a lesson"""
    updated_lesson = LessonRepository.update_lesson(session, lesson_id, lesson_update)
    if not updated_lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return updated_lesson

@router.delete("/lessons/{lesson_id}")
def delete_lesson(lesson_id: int, session: Session = Depends(get_session)):
    """Delete a lesson"""
    if not LessonRepository.delete_lesson(session, lesson_id):
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {"message": "Lesson deleted successfully"}

# ==================== QUIZ APIs ====================

@router.post("/quizzes/", response_model=QuizRead)
def create_quiz(quiz: QuizCreate, session: Session = Depends(get_session)):
    """Create a new quiz for a course"""
    return QuizRepository.create_quiz(session, quiz)

@router.get("/quizzes/{quiz_id}", response_model=QuizRead)
def get_quiz(quiz_id: int, session: Session = Depends(get_session)):
    """Get a specific quiz by ID"""
    quiz = QuizRepository.get_quiz_by_id(session, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.get("/courses/{course_id}/quizzes/", response_model=List[QuizRead])
def get_course_quizzes(course_id: int, session: Session = Depends(get_session)):
    """Get all quizzes for a specific course"""
    return QuizRepository.get_quizzes_by_course(session, course_id)

@router.put("/quizzes/{quiz_id}", response_model=QuizRead)
def update_quiz(quiz_id: int, quiz_update: QuizUpdate, session: Session = Depends(get_session)):
    """Update a quiz"""
    updated_quiz = QuizRepository.update_quiz(session, quiz_id, quiz_update)
    if not updated_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return updated_quiz

@router.delete("/quizzes/{quiz_id}")
def delete_quiz(quiz_id: int, session: Session = Depends(get_session)):
    """Delete a quiz"""
    if not QuizRepository.delete_quiz(session, quiz_id):
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {"message": "Quiz deleted successfully"}

# ==================== QUESTION APIs ====================

@router.post("/questions/", response_model=QuestionRead)
def create_question(question: QuestionCreate, session: Session = Depends(get_session)):
    """Create a new question for a quiz"""
    return QuestionRepository.create_question(session, question)

@router.get("/questions/{question_id}", response_model=QuestionRead)
def get_question(question_id: int, session: Session = Depends(get_session)):
    """Get a specific question by ID"""
    question = QuestionRepository.get_question_by_id(session, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.get("/quizzes/{quiz_id}/questions/", response_model=List[QuestionRead])
def get_quiz_questions(quiz_id: int, session: Session = Depends(get_session)):
    """Get all questions for a specific quiz"""
    return QuestionRepository.get_questions_by_quiz(session, quiz_id)

@router.put("/questions/{question_id}", response_model=QuestionRead)
def update_question(question_id: int, question_update: QuestionUpdate, session: Session = Depends(get_session)):
    """Update a question"""
    updated_question = QuestionRepository.update_question(session, question_id, question_update)
    if not updated_question:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated_question

@router.delete("/questions/{question_id}")
def delete_question(question_id: int, session: Session = Depends(get_session)):
    """Delete a question"""
    if not QuestionRepository.delete_question(session, question_id):
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}

# ==================== FLASHCARD APIs ====================

@router.post("/flashcards/", response_model=FlashcardRead)
def create_flashcard(flashcard: FlashcardCreate, session: Session = Depends(get_session)):
    """Create a new flashcard for a course"""
    return FlashcardRepository.create_flashcard(session, flashcard)

@router.get("/flashcards/{flashcard_id}", response_model=FlashcardRead)
def get_flashcard(flashcard_id: int, session: Session = Depends(get_session)):
    """Get a specific flashcard by ID"""
    flashcard = FlashcardRepository.get_flashcard_by_id(session, flashcard_id)
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return flashcard

@router.get("/courses/{course_id}/flashcards/", response_model=List[FlashcardRead])
def get_course_flashcards(course_id: int, session: Session = Depends(get_session)):
    """Get all flashcards for a specific course"""
    return FlashcardRepository.get_flashcards_by_course(session, course_id)

@router.put("/flashcards/{flashcard_id}", response_model=FlashcardRead)
def update_flashcard(flashcard_id: int, flashcard_update: FlashcardUpdate, session: Session = Depends(get_session)):
    """Update a flashcard"""
    updated_flashcard = FlashcardRepository.update_flashcard(session, flashcard_id, flashcard_update)
    if not updated_flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return updated_flashcard

@router.delete("/flashcards/{flashcard_id}")
def delete_flashcard(flashcard_id: int, session: Session = Depends(get_session)):
    """Delete a flashcard"""
    if not FlashcardRepository.delete_flashcard(session, flashcard_id):
        raise HTTPException(status_code=404, detail="Flashcard not found")
    return {"message": "Flashcard deleted successfully"}

# ==================== MINDMAP APIs ====================

@router.post("/mindmaps/", response_model=MindmapRead)
def create_mindmap(mindmap: MindmapCreate, session: Session = Depends(get_session)):
    """Create a new mindmap for a course"""
    return MindmapRepository.create_mindmap(session, mindmap)

@router.get("/mindmaps/{mindmap_id}", response_model=MindmapRead)
def get_mindmap(mindmap_id: int, session: Session = Depends(get_session)):
    """Get a specific mindmap by ID"""
    mindmap = MindmapRepository.get_mindmap_by_id(session, mindmap_id)
    if not mindmap:
        raise HTTPException(status_code=404, detail="Mindmap not found")
    return mindmap

@router.get("/courses/{course_id}/mindmaps/", response_model=List[MindmapRead])
def get_course_mindmaps(course_id: int, session: Session = Depends(get_session)):
    """Get all mindmaps for a specific course"""
    return MindmapRepository.get_mindmaps_by_course(session, course_id)

@router.put("/mindmaps/{mindmap_id}", response_model=MindmapRead)
def update_mindmap(mindmap_id: int, mindmap_update: MindmapUpdate, session: Session = Depends(get_session)):
    """Update a mindmap"""
    updated_mindmap = MindmapRepository.update_mindmap(session, mindmap_id, mindmap_update)
    if not updated_mindmap:
        raise HTTPException(status_code=404, detail="Mindmap not found")
    return updated_mindmap

@router.delete("/mindmaps/{mindmap_id}")
def delete_mindmap(mindmap_id: int, session: Session = Depends(get_session)):
    """Delete a mindmap"""
    if not MindmapRepository.delete_mindmap(session, mindmap_id):
        raise HTTPException(status_code=404, detail="Mindmap not found")
    return {"message": "Mindmap deleted successfully"}

# ==================== MEMORY GAME APIs ====================

@router.post("/memory-games/", response_model=MemoryGameRead)
def create_memory_game(memory_game: MemoryGameCreate, session: Session = Depends(get_session)):
    """Create a new memory game for a course"""
    return MemoryGameRepository.create_memory_game(session, memory_game)

@router.get("/memory-games/{memory_game_id}", response_model=MemoryGameRead)
def get_memory_game(memory_game_id: int, session: Session = Depends(get_session)):
    """Get a specific memory game by ID"""
    memory_game = MemoryGameRepository.get_memory_game_by_id(session, memory_game_id)
    if not memory_game:
        raise HTTPException(status_code=404, detail="Memory game not found")
    return memory_game

@router.get("/courses/{course_id}/memory-games/", response_model=List[MemoryGameRead])
def get_course_memory_games(course_id: int, session: Session = Depends(get_session)):
    """Get all memory games for a specific course"""
    return MemoryGameRepository.get_memory_games_by_course(session, course_id)

@router.put("/memory-games/{memory_game_id}", response_model=MemoryGameRead)
def update_memory_game(memory_game_id: int, memory_game_update: MemoryGameUpdate, session: Session = Depends(get_session)):
    """Update a memory game"""
    updated_memory_game = MemoryGameRepository.update_memory_game(session, memory_game_id, memory_game_update)
    if not updated_memory_game:
        raise HTTPException(status_code=404, detail="Memory game not found")
    return updated_memory_game

@router.delete("/memory-games/{memory_game_id}")
def delete_memory_game(memory_game_id: int, session: Session = Depends(get_session)):
    """Delete a memory game"""
    if not MemoryGameRepository.delete_memory_game(session, memory_game_id):
        raise HTTPException(status_code=404, detail="Memory game not found")
    return {"message": "Memory game deleted successfully"}

# ==================== TOPIC APIs ====================

@router.post("/topics/", response_model=TopicRead)
def create_topic(topic: TopicCreate, session: Session = Depends(get_session)):
    """Create a new topic for a course"""
    return TopicRepository.create_topic(session, topic)

@router.get("/topics/{topic_id}", response_model=TopicRead)
def get_topic(topic_id: int, session: Session = Depends(get_session)):
    """Get a specific topic by ID"""
    topic = TopicRepository.get_topic_by_id(session, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.get("/courses/{course_id}/topics/", response_model=List[TopicRead])
def get_course_topics(course_id: int, session: Session = Depends(get_session)):
    """Get all topics for a specific course"""
    return TopicRepository.get_topics_by_course(session, course_id)

@router.put("/topics/{topic_id}", response_model=TopicRead)
def update_topic(topic_id: int, topic_update: TopicUpdate, session: Session = Depends(get_session)):
    """Update a topic"""
    updated_topic = TopicRepository.update_topic(session, topic_id, topic_update)
    if not updated_topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return updated_topic

@router.delete("/topics/{topic_id}")
def delete_topic(topic_id: int, session: Session = Depends(get_session)):
    """Delete a topic"""
    if not TopicRepository.delete_topic(session, topic_id):
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"message": "Topic deleted successfully"}

# ==================== COURSE LEARNING OVERVIEW ====================

@router.get("/courses/{course_id}/learning-content/")
def get_course_learning_content(course_id: int, session: Session = Depends(get_session)):
    """Get comprehensive learning content for a course including lessons, quizzes, flashcards, etc."""
    try:
        # Get course details
        course = session.get(Course, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Get all learning content
        lessons = LessonRepository.get_lessons_by_course(session, course_id)
        quizzes = QuizRepository.get_quizzes_by_course(session, course_id)
        flashcards = FlashcardRepository.get_flashcards_by_course(session, course_id)
        mindmaps = MindmapRepository.get_mindmaps_by_course(session, course_id)
        memory_games = MemoryGameRepository.get_memory_games_by_course(session, course_id)
        topics = TopicRepository.get_topics_by_course(session, course_id)
        
        return {
            "course_id": course_id,
            "course_title": course.title,
            "learning_content": {
                "lessons": lessons,
                "quizzes": quizzes,
                "flashcards": flashcards,
                "mindmaps": mindmaps,
                "memory_games": memory_games,
                "topics": topics
            },
            "content_summary": {
                "total_lessons": len(lessons),
                "total_quizzes": len(quizzes),
                "total_flashcards": len(flashcards),
                "total_mindmaps": len(mindmaps),
                "total_memory_games": len(memory_games),
                "total_topics": len(topics)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving learning content: {str(e)}")
