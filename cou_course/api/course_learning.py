from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlalchemy import text
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
from cou_course.models.course import Course
from cou_course.models.course_learning import VideoListResponse, VideoInfo
from cou_course.schemas.lesson_schema import LessonCreate, LessonRead, LessonUpdate, LessonWithCourseInfo
from cou_course.schemas.quiz_schema import QuizCreate, QuizRead, QuizUpdate
from cou_course.schemas.question_schema import QuestionCreate, QuestionRead, QuestionUpdate
from cou_course.schemas.flashcard_schema import FlashcardCreate, FlashcardRead, FlashcardUpdate
from cou_course.schemas.mindmap_schema import MindmapCreate, MindmapRead, MindmapUpdate
from cou_course.schemas.memory_game_schema import MemoryGameCreate, MemoryGameRead, MemoryGameUpdate
from cou_course.schemas.topic_schema import TopicCreate, TopicRead, TopicUpdate
from cou_course.schemas.course_schema import CourseDetailsRead
from cou_course.models.question import QuestionType
from cou_course.repositories.lesson_repository import LessonRepository
from cou_course.repositories.quiz_repository import QuizRepository
from cou_course.repositories.question_repository import QuestionRepository
from cou_course.repositories.flashcard_repository import FlashcardRepository
from cou_course.repositories.mindmap_repository import MindmapRepository
from cou_course.repositories.memory_game_repository import MemoryGameRepository
from cou_course.repositories.topic_repository import TopicRepository
from cou_course.repositories.course_repository import CourseRepository




# Azure Blob Storage setup - make it conditional for Vercel
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Azure Blob Storage setup - make it conditional for Vercel
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
CONTAINER_NAME = "lessons"  # You can change this to your preferred container name

# Initialize Azure services only if connection string is available
blob_service_client = None
container_client = None

def _init_azure_services():
    """Initialize Azure services if connection string is available"""
    global blob_service_client, container_client
    
    if not AZURE_CONNECTION_STRING:
        logger.warning("AZURE_STORAGE_CONNECTION_STRING not set, Azure features will be disabled")
        return False
    
    try:
        # Import Azure modules only when needed - moved inside function to avoid module-level import errors
        import importlib.util
        
        # Check if azure module is available
        azure_spec = importlib.util.find_spec("azure.storage.blob")
        if not azure_spec:
            logger.warning("Azure modules not available")
            return False
            
        from azure.storage.blob import BlobServiceClient
        from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
        
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        # Get the container client
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        # Verify container exists
        if not container_client.exists():
            logger.warning(f"Container '{CONTAINER_NAME}' does not exist in Azure Storage")
            container_client = None
            return False
        
        logger.info("Azure Blob Service Client initialized successfully")
        return True
        
    except ImportError as e:
        logger.warning(f"Azure modules not available: {e}")
        return False
    except Exception as e:
        logger.warning(f"Failed to initialize Azure Blob Service Client: {str(e)}")
        return False

# Try to initialize Azure services
_init_azure_services()

router = APIRouter(
    prefix="/course-learning",
    tags=["Course Learning"]
)

# ==================== VIDEO URL APIs ====================

@router.get("/videos/", response_model=VideoListResponse)
def fetch_videos():
    """Get all videos from Azure Blob Storage"""
    if not container_client or not blob_service_client:
        logger.warning("Azure services not available, returning empty video list")
        return VideoListResponse(videos=[])
    
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
    if not container_client or not blob_service_client:
        logger.warning("Azure services not available")
        raise HTTPException(status_code=503, detail="Video service temporarily unavailable")
    
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
    if not container_client or not blob_service_client:
        logger.warning("Azure services not available")
        raise HTTPException(status_code=503, detail="Video service temporarily unavailable")
    
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
    if not container_client or not blob_service_client:
        logger.warning("Azure services not available, returning empty lesson list")
        return {"lessons": []}
    
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

# ==================== COURSE DETAILS APIs ====================

@router.get("/courses/{course_id}/details", response_model=CourseDetailsRead)
def get_course_details(course_id: int, session: Session = Depends(get_session)):
    """Get comprehensive course details by course ID"""
    try:
        # First try the normal SQLModel approach
        if hasattr(session, 'exec'):  # This is a SQLModel session
            course = CourseRepository.get_course_details_by_id(session, course_id)
    
            if not course:
                raise HTTPException(status_code=404, detail="Course not found")
            
            # Convert Course model to CourseDetailsRead schema
            course_dict = course.dict()
            
            # Add instructor information if available
            instructor_info = None
            if hasattr(course, 'mentor') and course.mentor:
                instructor_info = {
                    "id": course.mentor.user_id,
                    "display_name": f"{course.mentor.first_name} {course.mentor.last_name}".strip(),
                    "first_name": course.mentor.first_name,
                    "last_name": course.mentor.last_name
                }
            
            course_dict["instructor"] = instructor_info
            
            return CourseDetailsRead(**course_dict)
        else:
           
            return None
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get course details for course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get course details: {str(e)}")

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
        # First try the normal SQLModel approach
        if hasattr(session, 'exec'):  # This is a SQLModel session
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
        else:
            # Fallback for simple database connection (in-memory SQLite)
            logger.info("Using fallback implementation for simple database tables")
            
            # Simple query to get lessons
            result = session.execute(text("""
                SELECT id, course_id, title, content, 1 as active 
                FROM lesson 
                WHERE course_id = :course_id AND active = 1
            """), {"course_id": course_id})
            
            lessons = []
            from datetime import datetime, timezone
            
            for row in result.fetchall():
                current_time = datetime.now(timezone.utc)
                lesson_data = {
                    "id": row[0],
                    "course_id": row[1],
                    "title": row[2] or "Sample Lesson",
                    "content": row[3] or "Sample content for the lesson",
                    "active": bool(row[4]),
                    "topic_id": 1,  # Default topic ID
                    "created_at": current_time,  # Keep as datetime object
                    "created_by": 1,  # Default user ID
                    "updated_at": current_time,  # Keep as datetime object
                    "updated_by": 1,  # Default user ID
                    "video_source": None,
                    "video_path": None,
                    "video_filename": None,
                    "image_path": None,
                    "is_completed": False,
                    "code": None,
                    "code_language": None,
                    "code_output": None,
                    "course_code": "SAMPLE",
                    "course_code_language": "python"
                }
                
                logger.info(f"Lesson data being created: {lesson_data}")
                
                try:
                    lesson_obj = LessonWithCourseInfo(**lesson_data)
                    lessons.append(lesson_obj)
                    logger.info(f"Successfully created lesson object: {lesson_obj.id}")
                except Exception as validation_error:
                    logger.error(f"Validation error for lesson data: {validation_error}")
                    logger.error(f"Failed data: {lesson_data}")
                    # Continue with other lessons
                    continue
            
            return lessons
            
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
    try:
        # First try the normal SQLModel approach
        if hasattr(session, 'exec'):  # This is a SQLModel session
            return QuizRepository.get_quizzes_by_course(session, course_id)
        else:
            # Fallback for simple database connection (in-memory SQLite)
            logger.info("Using fallback implementation for quizzes with simple database tables")
            
            # Simple query to get quizzes
            result = session.execute(text("""
                SELECT id, course_id, title, description, 1 as active 
                FROM quiz 
                WHERE course_id = :course_id AND active = 1
            """), {"course_id": course_id})
            
            quizzes = []
            from datetime import datetime, timezone
            
            for row in result.fetchall():
                current_time = datetime.now(timezone.utc)
                quiz_data = {
                    "id": row[0],
                    "course_id": row[1],
                    "title": row[2] or "Sample Quiz",
                    "description": row[3] or "Sample quiz description",
                    "active": bool(row[4]),
                    "topic_id": 1,  # Default topic ID
                    "time_limit_minutes": 30,  # Default time limit
                    "max_questions": 10,  # Default max questions
                    "passing_grade_percent": 70,  # Default passing grade
                    "is_completed": False,
                    "created_at": current_time,
                    "created_by": 1,
                    "updated_at": current_time,
                    "updated_by": 1
                }
                
                try:
                    quiz_obj = QuizRead(**quiz_data)
                    quizzes.append(quiz_obj)
                    logger.info(f"Successfully created quiz object: {quiz_obj.id}")
                except Exception as validation_error:
                    logger.error(f"Validation error for quiz data: {validation_error}")
                    continue
            
            return quizzes
            
    except Exception as e:
        logger.error(f"Failed to get quizzes for course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get quizzes: {str(e)}")

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
    try:
        # First try the normal SQLModel approach
        if hasattr(session, 'exec'):  # This is a SQLModel session
            return QuestionRepository.get_questions_by_quiz(session, quiz_id)
        else:
            # Fallback for simple database connection (in-memory SQLite)
            logger.info("Using fallback implementation for questions with simple database tables")
            
            # Simple query to get questions
            result = session.execute(text("""
                SELECT id, quiz_id, question_text, question_type, 1 as active 
                FROM question 
                WHERE quiz_id = :quiz_id AND active = 1
            """), {"quiz_id": quiz_id})
            
            questions = []
            from datetime import datetime, timezone
            
            for row in result.fetchall():
                current_time = datetime.now(timezone.utc)
                
                # Map database question_type values to enum values
                question_type_mapping = {
                    "True/False": QuestionType.TRUE_FALSE,
                    "true/false": QuestionType.TRUE_FALSE,
                    "TRUE_FALSE": QuestionType.TRUE_FALSE,
                    "Multiple Choice": QuestionType.MULTIPLE,
                    "multiple_choice": QuestionType.MULTIPLE,
                    "MULTIPLE": QuestionType.MULTIPLE,
                    "Single Choice": QuestionType.SINGLE,
                    "single_choice": QuestionType.SINGLE,
                    "SINGLE": QuestionType.SINGLE,
                    "Fill in the Blank": QuestionType.FILL_BLANK,
                    "fill_blank": QuestionType.FILL_BLANK,
                    "FILL_BLANK": QuestionType.FILL_BLANK,
                    "Open Ended": QuestionType.OPEN_ENDED,
                    "open_ended": QuestionType.OPEN_ENDED,
                    "OPEN_ENDED": QuestionType.OPEN_ENDED,
                    "Matching Text": QuestionType.MATCHING_TEXT,
                    "matching_text": QuestionType.MATCHING_TEXT,
                    "MATCHING_TEXT": QuestionType.MATCHING_TEXT,
                    "Matching Image": QuestionType.MATCHING_IMAGE,
                    "matching_image": QuestionType.MATCHING_IMAGE,
                    "MATCHING_IMAGE": QuestionType.MATCHING_IMAGE,
                    "Sort Answer": QuestionType.SORT_ANSWER,
                    "sort_answer": QuestionType.SORT_ANSWER,
                    "SORT_ANSWER": QuestionType.SORT_ANSWER
                }
                
                # Get the mapped question type or default to SINGLE
                db_question_type = row[3] or "SINGLE"
                mapped_question_type = question_type_mapping.get(db_question_type, QuestionType.SINGLE)
                
                # Debug logging
                logger.info(f"Database question_type: '{db_question_type}', Mapped to: '{mapped_question_type}'")
                
                question_data = {
                    "id": row[0],
                    "quiz_id": row[1],
                    "question_text": row[2] or "Sample Question",
                    "type": mapped_question_type,  # Use 'type' instead of 'question_type'
                    "points": 1,  # Default points
                    "answers": None,  # Default answers
                    "question_order": None,  # Default order
                    "active": bool(row[4]),
                    "created_at": current_time,
                    "created_by": 1,
                    "updated_at": current_time,
                    "updated_by": 1
                }
                
                try:
                    question_obj = QuestionRead(**question_data)
                    questions.append(question_obj)
                    logger.info(f"Successfully created question object: {question_obj.id}")
                except Exception as validation_error:
                    logger.error(f"Validation error for question data: {validation_error}")
                    continue
            
            return questions
            
    except Exception as e:
        logger.error(f"Failed to get questions for quiz {quiz_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get questions: {str(e)}")

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
    try:
        # First try the normal SQLModel approach
        if hasattr(session, 'exec'):  # This is a SQLModel session
            return FlashcardRepository.get_flashcards_by_course(session, course_id)
        else:
            # Fallback for simple database connection (in-memory SQLite)
            logger.info("Using fallback implementation for flashcards with simple database tables")
            
            # Simple query to get flashcards
            result = session.execute(text("""
                SELECT id, course_id, topic_id, flashcard_set_id, front, back, clue, card_order, is_completed, active 
                FROM flashcard 
                WHERE course_id = :course_id AND active = 1
            """), {"course_id": course_id})
            
            flashcards = []
            from datetime import datetime, timezone
            
            for row in result.fetchall():
                current_time = datetime.now(timezone.utc)
                flashcard_data = {
                    "id": row[0],
                    "course_id": row[1],
                    "topic_id": row[2],
                    "flashcard_set_id": row[3],
                    "front": row[4] or "Sample Question",
                    "back": row[5] or "Sample Answer",
                    "clue": row[6],
                    "card_order": row[7] or 1,
                    "is_completed": bool(row[8]),
                    "active": bool(row[9]),
                    "created_at": current_time,
                    "created_by": 1,
                    "updated_at": current_time,
                    "updated_by": 1
                }
                
                try:
                    flashcard_obj = FlashcardRead(**flashcard_data)
                    flashcards.append(flashcard_obj)
                    logger.info(f"Successfully created flashcard object: {flashcard_obj.id}")
                except Exception as validation_error:
                    logger.error(f"Validation error for flashcard data: {validation_error}")
                    continue
            
            return flashcards
            
    except Exception as e:
        logger.error(f"Failed to get flashcards for course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get flashcards: {str(e)}")

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
    try:
        # First try the normal SQLModel approach
        if hasattr(session, 'exec'):  # This is a SQLModel session
            return MindmapRepository.get_mindmaps_by_course(session, course_id)
        else:
            # Fallback for simple database connection (in-memory SQLite)
            logger.info("Using fallback implementation for mindmaps with simple database tables")
            
            # Simple query to get mindmaps
            result = session.execute(text("""
                SELECT id, course_id, topic_id, title, description, content, mindmap_mermaid, mindmap_json, is_completed, active 
                FROM mindmap 
                WHERE course_id = :course_id AND active = 1
            """), {"course_id": course_id})
            
            mindmaps = []
            from datetime import datetime, timezone
            
            for row in result.fetchall():
                current_time = datetime.now(timezone.utc)
                mindmap_data = {
                    "id": row[0],
                    "course_id": row[1],
                    "topic_id": row[2],
                    "title": row[3] or "Sample Mindmap",
                    "description": row[4] or "Sample mindmap description",
                    "content": row[5] or "{}",  # Default empty JSON
                    "active": bool(row[9]),
                    "mindmap_mermaid": row[6],  # Optional field
                    "mindmap_json": {"nodes": [{"id": "1", "label": "Sample Node"}]} if not row[7] else row[7],  # Required field
                    "is_completed": bool(row[8]),  # Default value
                    "created_at": current_time,
                    "created_by": 1,
                    "updated_at": current_time,
                    "updated_by": 1
                }
                
                try:
                    mindmap_obj = MindmapRead(**mindmap_data)
                    mindmaps.append(mindmap_obj)
                    logger.info(f"Successfully created mindmap object: {mindmap_obj.id}")
                except Exception as validation_error:
                    logger.error(f"Validation error for mindmap data: {validation_error}")
                    continue
            
            return mindmaps
            
    except Exception as e:
        logger.error(f"Failed to get mindmaps for course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get mindmaps: {str(e)}")

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
    try:
        # First try the normal SQLModel approach
        if hasattr(session, 'exec'):  # This is a SQLModel session
            return MemoryGameRepository.get_memory_games_by_course(session, course_id)
        else:
            # Fallback for simple database connection (in-memory SQLite)
            logger.info("Using fallback implementation for memory games with simple database tables")
            
            # Simple query to get memory games
            result = session.execute(text("""
                SELECT id, course_id, topic_id, title, description, is_completed, active 
                FROM memory_game 
                WHERE course_id = :course_id AND active = 1
            """), {"course_id": course_id})
            
            memory_games = []
            from datetime import datetime, timezone
            
            for row in result.fetchall():
                current_time = datetime.now(timezone.utc)
                memory_game_data = {
                    "id": row[0],
                    "course_id": row[1],
                    "topic_id": row[2],
                    "title": row[3] or "Sample Memory Game",
                    "description": row[4] or "Sample memory game description",
                    "active": bool(row[6]),
                    "is_completed": bool(row[5]),
                    "created_at": current_time,
                    "created_by": 1,
                    "updated_at": current_time,
                    "updated_by": 1
                }
                
                try:
                    memory_game_obj = MemoryGameRead(**memory_game_data)
                    memory_games.append(memory_game_obj)
                    logger.info(f"Successfully created memory game object: {memory_game_obj.id}")
                except Exception as validation_error:
                    logger.error(f"Validation error for memory game data: {validation_error}")
                    continue
            
            return memory_games
            
    except Exception as e:
        logger.error(f"Failed to get memory games for course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get memory games: {str(e)}")

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
    try:
        # First try the normal SQLModel approach
        if hasattr(session, 'exec'):  # This is a SQLModel session
            return TopicRepository.get_topics_by_course(session, course_id)
        else:
            # Fallback for simple database connection (in-memory SQLite)
            logger.info("Using fallback implementation for topics with simple database tables")
            
            # Simple query to get topics
            result = session.execute(text("""
                SELECT id, course_id, title, 1 as active 
                FROM topic 
                WHERE course_id = :course_id AND active = 1
            """), {"course_id": course_id})
            
            topics = []
            from datetime import datetime, timezone
            
            for row in result.fetchall():
                current_time = datetime.now(timezone.utc)
                topic_data = {
                    "id": row[0],
                    "course_id": row[1],
                    "title": row[2] or "Sample Topic",
                    "active": bool(row[3]),
                    "created_at": current_time,
                    "created_by": 1,
                    "updated_at": current_time,
                    "updated_by": 1
                }
                
                try:
                    topic_obj = TopicRead(**topic_data)
                    topics.append(topic_obj)
                    logger.info(f"Successfully created topic object: {topic_obj.id}")
                except Exception as validation_error:
                    logger.error(f"Validation error for topic data: {validation_error}")
                    continue
            
            return topics
            
    except Exception as e:
        logger.error(f"Failed to get topics for course {course_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get topics: {str(e)}")

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
        # First try the normal SQLModel approach
        if hasattr(session, 'exec'):  # This is a SQLModel session
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
        else:
            # Fallback for simple database connection (in-memory SQLite)
            logger.info("Using fallback implementation for course learning content with simple database tables")
            
            # Get course info
            course_result = session.execute(text("""
                SELECT title FROM course WHERE id = :course_id AND active = 1
            """), {"course_id": course_id})
            
            course_row = course_result.fetchone()
            if not course_row:
                raise HTTPException(status_code=404, detail="Course not found")
            
            course_title = course_row[0] or "Sample Course"
            
            # Get counts from each table
            lessons_result = session.execute(text("SELECT COUNT(*) FROM lesson WHERE course_id = :course_id AND active = 1"), {"course_id": course_id})
            quizzes_result = session.execute(text("SELECT COUNT(*) FROM quiz WHERE course_id = :course_id AND active = 1"), {"course_id": course_id})
            flashcards_result = session.execute(text("SELECT COUNT(*) FROM flashcard WHERE course_id = :course_id AND active = 1"), {"course_id": course_id})
            mindmaps_result = session.execute(text("SELECT COUNT(*) FROM mindmap WHERE course_id = :course_id AND active = 1"), {"course_id": course_id})
            memory_games_result = session.execute(text("SELECT COUNT(*) FROM memory_game WHERE course_id = :course_id AND active = 1"), {"course_id": course_id})
            topics_result = session.execute(text("SELECT COUNT(*) FROM topic WHERE course_id = :course_id AND active = 1"), {"course_id": course_id})
            
            total_lessons = lessons_result.fetchone()[0]
            total_quizzes = quizzes_result.fetchone()[0]
            total_flashcards = flashcards_result.fetchone()[0]
            total_mindmaps = mindmaps_result.fetchone()[0]
            total_memory_games = memory_games_result.fetchone()[0]
            total_topics = topics_result.fetchone()[0]
            
            return {
                "course_id": course_id,
                "course_title": course_title,
                "learning_content": {
                    "lessons": [],
                    "quizzes": [],
                    "flashcards": [],
                    "mindmaps": [],
                    "memory_games": [],
                    "topics": []
                },
                "content_summary": {
                    "total_lessons": total_lessons,
                    "total_quizzes": total_quizzes,
                    "total_flashcards": total_flashcards,
                    "total_mindmaps": total_mindmaps,
                    "total_memory_games": total_memory_games,
                    "total_topics": total_topics
                }
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving learning content: {str(e)}")
