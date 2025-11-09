"""
Integration tests for database operations.

This module tests CRUD operations for all models, complex queries with joins,
transaction rollbacks, and error handling.

Requirements: All requirements
"""

import pytest
from datetime import date, datetime
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.exc import IntegrityError, DataError
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import (
    Role, User, Project, ProjectStage, DefectStatus, Defect,
    Comment, Attachment, HistoryLog, Report, PriorityEnum, ActionTypeEnum
)


class TestRoleCRUD:
    """Integration tests for Role CRUD operations."""
    
    def test_create_role(self, db_session: Session):
        """Test creating a role in the database."""
        role = Role(name="Admin", description="Administrator role")
        db_session.add(role)
        db_session.commit()
        
        # Query back from database
        queried_role = db_session.query(Role).filter_by(name="Admin").first()
        assert queried_role is not None
        assert queried_role.name == "Admin"
        assert queried_role.description == "Administrator role"
    
    def test_read_role(self, db_session: Session, sample_role: Role):
        """Test reading a role from the database."""
        role = db_session.query(Role).filter_by(id=sample_role.id).first()
        assert role is not None
        assert role.id == sample_role.id
        assert role.name == sample_role.name
    
    def test_update_role(self, db_session: Session, sample_role: Role):
        """Test updating a role in the database."""
        sample_role.description = "Updated description"
        db_session.commit()
        
        # Query back to verify update
        updated_role = db_session.query(Role).filter_by(id=sample_role.id).first()
        assert updated_role.description == "Updated description"
    
    def test_delete_role(self, db_session: Session):
        """Test deleting a role from the database."""
        role = Role(name="Temporary", description="Temporary role")
        db_session.add(role)
        db_session.commit()
        role_id = role.id
        
        # Delete the role
        db_session.delete(role)
        db_session.commit()
        
        # Verify deletion
        deleted_role = db_session.query(Role).filter_by(id=role_id).first()
        assert deleted_role is None


class TestUserCRUD:
    """Integration tests for User CRUD operations."""
    
    def test_create_user(self, db_session: Session, sample_role: Role):
        """Test creating a user in the database."""
        user = User(
            full_name="Alice Smith",
            email="alice@example.com",
            password_hash="hashed_pass",
            role_id=sample_role.id
        )
        db_session.add(user)
        db_session.commit()
        
        queried_user = db_session.query(User).filter_by(email="alice@example.com").first()
        assert queried_user is not None
        assert queried_user.full_name == "Alice Smith"
        assert queried_user.is_active is True
    
    def test_read_user_with_role(self, db_session: Session, sample_user: User):
        """Test reading a user with role relationship."""
        user = db_session.query(User).options(joinedload(User.role)).filter_by(id=sample_user.id).first()
        assert user is not None
        assert user.role is not None
        assert user.role.name == "Engineer"
    
    def test_update_user(self, db_session: Session, sample_user: User):
        """Test updating a user in the database."""
        sample_user.full_name = "John Updated"
        sample_user.is_active = False
        db_session.commit()
        
        updated_user = db_session.query(User).filter_by(id=sample_user.id).first()
        assert updated_user.full_name == "John Updated"
        assert updated_user.is_active is False
    
    def test_delete_user_with_no_dependencies(self, db_session: Session, sample_role: Role):
        """Test deleting a user with no dependencies."""
        user = User(
            full_name="Temp User",
            email="temp@example.com",
            password_hash="hash",
            role_id=sample_role.id
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        db_session.delete(user)
        db_session.commit()
        
        deleted_user = db_session.query(User).filter_by(id=user_id).first()
        assert deleted_user is None


class TestProjectCRUD:
    """Integration tests for Project CRUD operations."""
    
    def test_create_project(self, db_session: Session, sample_user: User):
        """Test creating a project in the database."""
        project = Project(
            name="New Building",
            description="Construction project",
            manager_id=sample_user.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        db_session.add(project)
        db_session.commit()
        
        queried_project = db_session.query(Project).filter_by(name="New Building").first()
        assert queried_project is not None
        assert queried_project.manager_id == sample_user.id
    
    def test_read_project_with_manager(self, db_session: Session, sample_project: Project):
        """Test reading a project with manager relationship."""
        project = db_session.query(Project).options(joinedload(Project.manager)).filter_by(id=sample_project.id).first()
        assert project is not None
        assert project.manager is not None
        assert project.manager.email == "john.doe@example.com"
    
    def test_update_project(self, db_session: Session, sample_project: Project):
        """Test updating a project in the database."""
        sample_project.name = "Updated Project Name"
        sample_project.end_date = date(2025, 6, 30)
        db_session.commit()
        
        updated_project = db_session.query(Project).filter_by(id=sample_project.id).first()
        assert updated_project.name == "Updated Project Name"
        assert updated_project.end_date == date(2025, 6, 30)
    
    def test_delete_project_cascades_to_stages(self, db_session: Session, sample_project: Project):
        """Test that deleting a project cascades to project stages."""
        stage = ProjectStage(
            project_id=sample_project.id,
            name="Foundation",
            description="Foundation work"
        )
        db_session.add(stage)
        db_session.commit()
        stage_id = stage.id
        
        db_session.delete(sample_project)
        db_session.commit()
        
        deleted_stage = db_session.query(ProjectStage).filter_by(id=stage_id).first()
        assert deleted_stage is None


class TestDefectCRUD:
    """Integration tests for Defect CRUD operations."""
    
    def test_create_defect(self, db_session: Session, sample_project: Project, 
                          sample_defect_status: DefectStatus, sample_user: User):
        """Test creating a defect in the database."""
        defect = Defect(
            project_id=sample_project.id,
            title="Wall crack",
            description="Visible crack in wall",
            priority=PriorityEnum.CRITICAL,
            status_id=sample_defect_status.id,
            created_by=sample_user.id,
            due_date=date(2024, 6, 30)
        )
        db_session.add(defect)
        db_session.commit()
        
        queried_defect = db_session.query(Defect).filter_by(title="Wall crack").first()
        assert queried_defect is not None
        assert queried_defect.priority == PriorityEnum.CRITICAL
    
    def test_read_defect_with_relationships(self, db_session: Session, sample_defect: Defect):
        """Test reading a defect with all relationships."""
        defect = (
            db_session.query(Defect)
            .options(
                joinedload(Defect.project),
                joinedload(Defect.status),
                joinedload(Defect.creator)
            )
            .filter_by(id=sample_defect.id)
            .first()
        )
        assert defect is not None
        assert defect.project is not None
        assert defect.status is not None
        assert defect.creator is not None
    
    def test_update_defect(self, db_session: Session, sample_defect: Defect):
        """Test updating a defect in the database."""
        sample_defect.title = "Updated Defect Title"
        sample_defect.priority = PriorityEnum.LOW
        db_session.commit()
        
        updated_defect = db_session.query(Defect).filter_by(id=sample_defect.id).first()
        assert updated_defect.title == "Updated Defect Title"
        assert updated_defect.priority == PriorityEnum.LOW
    
    def test_delete_defect_cascades_to_children(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test that deleting a defect cascades to comments, attachments, and history logs."""
        # Add related entities
        comment = Comment(defect_id=sample_defect.id, user_id=sample_user.id, text="Test comment")
        attachment = Attachment(
            defect_id=sample_defect.id,
            uploaded_by=sample_user.id,
            file_name="test.jpg",
            file_path="/uploads/test.jpg"
        )
        history = HistoryLog(
            defect_id=sample_defect.id,
            user_id=sample_user.id,
            action_type=ActionTypeEnum.CREATE,
            new_value="Created"
        )
        db_session.add_all([comment, attachment, history])
        db_session.commit()
        
        comment_id = comment.id
        attachment_id = attachment.id
        history_id = history.id
        
        # Delete defect
        db_session.delete(sample_defect)
        db_session.commit()
        
        # Verify cascade deletion
        assert db_session.query(Comment).filter_by(id=comment_id).first() is None
        assert db_session.query(Attachment).filter_by(id=attachment_id).first() is None
        assert db_session.query(HistoryLog).filter_by(id=history_id).first() is None


class TestComplexQueries:
    """Integration tests for complex queries with joins."""
    
    def test_query_defects_by_project_and_status(self, db_session: Session, sample_project: Project,
                                                  sample_defect_status: DefectStatus, sample_user: User):
        """Test querying defects filtered by project and status."""
        # Create multiple defects
        defect1 = Defect(
            project_id=sample_project.id,
            title="Defect 1",
            priority=PriorityEnum.HIGH,
            status_id=sample_defect_status.id,
            created_by=sample_user.id
        )
        defect2 = Defect(
            project_id=sample_project.id,
            title="Defect 2",
            priority=PriorityEnum.MEDIUM,
            status_id=sample_defect_status.id,
            created_by=sample_user.id
        )
        db_session.add_all([defect1, defect2])
        db_session.commit()
        
        # Query defects by project and status
        defects = (
            db_session.query(Defect)
            .filter(
                and_(
                    Defect.project_id == sample_project.id,
                    Defect.status_id == sample_defect_status.id
                )
            )
            .all()
        )
        
        assert len(defects) == 2
        assert all(d.project_id == sample_project.id for d in defects)
        assert all(d.status_id == sample_defect_status.id for d in defects)
    
    def test_query_defects_with_priority_filter(self, db_session: Session, sample_project: Project,
                                                sample_defect_status: DefectStatus, sample_user: User):
        """Test querying defects filtered by priority."""
        # Create defects with different priorities
        for priority in [PriorityEnum.LOW, PriorityEnum.MEDIUM, PriorityEnum.HIGH, PriorityEnum.CRITICAL]:
            defect = Defect(
                project_id=sample_project.id,
                title=f"Defect {priority.value}",
                priority=priority,
                status_id=sample_defect_status.id,
                created_by=sample_user.id
            )
            db_session.add(defect)
        db_session.commit()
        
        # Query high and critical priority defects
        high_priority_defects = (
            db_session.query(Defect)
            .filter(Defect.priority.in_([PriorityEnum.HIGH, PriorityEnum.CRITICAL]))
            .all()
        )
        
        assert len(high_priority_defects) == 2
        assert all(d.priority in [PriorityEnum.HIGH, PriorityEnum.CRITICAL] for d in high_priority_defects)
    
    def test_query_defects_with_creator_join(self, db_session: Session, sample_project: Project,
                                            sample_defect_status: DefectStatus, sample_user: User, sample_role: Role):
        """Test querying defects with join to creator user."""
        defect = Defect(
            project_id=sample_project.id,
            title="Test Defect",
            priority=PriorityEnum.MEDIUM,
            status_id=sample_defect_status.id,
            created_by=sample_user.id
        )
        db_session.add(defect)
        db_session.commit()
        
        # Query with join
        result = (
            db_session.query(Defect, User)
            .join(User, Defect.created_by == User.id)
            .filter(Defect.id == defect.id)
            .first()
        )
        
        assert result is not None
        queried_defect, creator = result
        assert queried_defect.id == defect.id
        assert creator.id == sample_user.id
        assert creator.email == sample_user.email
    
    def test_query_project_with_defect_count(self, db_session: Session, sample_project: Project,
                                            sample_defect_status: DefectStatus, sample_user: User):
        """Test querying projects with defect count aggregation."""
        # Create multiple defects for the project
        for i in range(5):
            defect = Defect(
                project_id=sample_project.id,
                title=f"Defect {i}",
                priority=PriorityEnum.MEDIUM,
                status_id=sample_defect_status.id,
                created_by=sample_user.id
            )
            db_session.add(defect)
        db_session.commit()
        
        # Query with count
        result = (
            db_session.query(Project, func.count(Defect.id).label("defect_count"))
            .outerjoin(Defect, Project.id == Defect.project_id)
            .filter(Project.id == sample_project.id)
            .group_by(Project.id)
            .first()
        )
        
        assert result is not None
        project, defect_count = result
        assert project.id == sample_project.id
        assert defect_count == 5
    
    def test_query_defects_with_comments_count(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test querying defects with comment count."""
        # Add comments to defect
        for i in range(3):
            comment = Comment(
                defect_id=sample_defect.id,
                user_id=sample_user.id,
                text=f"Comment {i}"
            )
            db_session.add(comment)
        db_session.commit()
        
        # Query with comment count
        result = (
            db_session.query(Defect, func.count(Comment.id).label("comment_count"))
            .outerjoin(Comment, Defect.id == Comment.defect_id)
            .filter(Defect.id == sample_defect.id)
            .group_by(Defect.id)
            .first()
        )
        
        assert result is not None
        defect, comment_count = result
        assert defect.id == sample_defect.id
        assert comment_count == 3
    
    def test_query_users_with_assigned_defects(self, db_session: Session, sample_project: Project,
                                               sample_defect_status: DefectStatus, sample_user: User):
        """Test querying users with their assigned defects."""
        # Create defects assigned to user
        for i in range(2):
            defect = Defect(
                project_id=sample_project.id,
                title=f"Assigned Defect {i}",
                priority=PriorityEnum.HIGH,
                status_id=sample_defect_status.id,
                created_by=sample_user.id,
                assigned_to=sample_user.id
            )
            db_session.add(defect)
        db_session.commit()
        
        # Query user with assigned defects
        user = (
            db_session.query(User)
            .options(selectinload(User.assigned_defects))
            .filter_by(id=sample_user.id)
            .first()
        )
        
        assert user is not None
        assert len(user.assigned_defects) == 2
        assert all(d.assigned_to == sample_user.id for d in user.assigned_defects)
    
    def test_query_defects_ordered_by_priority_and_date(self, db_session: Session, sample_project: Project,
                                                        sample_defect_status: DefectStatus, sample_user: User):
        """Test querying defects with ordering."""
        # Create defects with different priorities and dates
        defects_data = [
            ("Defect 1", PriorityEnum.LOW, date(2024, 6, 1)),
            ("Defect 2", PriorityEnum.CRITICAL, date(2024, 5, 1)),
            ("Defect 3", PriorityEnum.HIGH, date(2024, 4, 1)),
        ]
        
        for title, priority, due_date in defects_data:
            defect = Defect(
                project_id=sample_project.id,
                title=title,
                priority=priority,
                status_id=sample_defect_status.id,
                created_by=sample_user.id,
                due_date=due_date
            )
            db_session.add(defect)
        db_session.commit()
        
        # Query ordered by due date
        defects = (
            db_session.query(Defect)
            .filter(Defect.project_id == sample_project.id)
            .order_by(Defect.due_date)
            .all()
        )
        
        assert len(defects) == 3
        assert defects[0].due_date == date(2024, 4, 1)
        assert defects[1].due_date == date(2024, 5, 1)
        assert defects[2].due_date == date(2024, 6, 1)


class TestTransactionRollback:
    """Integration tests for transaction rollbacks and error handling."""
    
    def test_rollback_on_constraint_violation(self, db_session: Session, sample_role: Role):
        """Test that transaction rolls back on constraint violation."""
        # Create a user
        user = User(
            full_name="Test User",
            email="test@example.com",
            password_hash="hash",
            role_id=sample_role.id
        )
        db_session.add(user)
        db_session.commit()
        
        # Try to create duplicate user
        duplicate_user = User(
            full_name="Duplicate",
            email="test@example.com",  # Same email
            password_hash="hash",
            role_id=sample_role.id
        )
        db_session.add(duplicate_user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        # Rollback the transaction
        db_session.rollback()
        
        # Verify original user still exists
        existing_user = db_session.query(User).filter_by(email="test@example.com").first()
        assert existing_user is not None
        assert existing_user.full_name == "Test User"
    
    def test_rollback_on_foreign_key_violation(self, db_session: Session):
        """Test that transaction rolls back on foreign key violation."""
        # Try to create defect with non-existent project
        defect = Defect(
            project_id=99999,  # Non-existent project
            title="Invalid Defect",
            priority=PriorityEnum.LOW,
            status_id=1,
            created_by=1
        )
        db_session.add(defect)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Verify no defect was created
        defects = db_session.query(Defect).all()
        assert len(defects) == 0
    
    def test_explicit_rollback(self, db_session: Session, sample_role: Role):
        """Test explicit transaction rollback."""
        # Create a user
        user = User(
            full_name="Rollback User",
            email="rollback@example.com",
            password_hash="hash",
            role_id=sample_role.id
        )
        db_session.add(user)
        db_session.flush()  # Flush but don't commit
        
        # Verify user is in session
        assert user in db_session
        
        # Rollback
        db_session.rollback()
        
        # Verify user was not persisted
        rolled_back_user = db_session.query(User).filter_by(email="rollback@example.com").first()
        assert rolled_back_user is None
    
    def test_partial_commit_rollback(self, db_session: Session, sample_role: Role):
        """Test rollback after partial operations."""
        # Create first user and commit
        user1 = User(
            full_name="User 1",
            email="user1@example.com",
            password_hash="hash",
            role_id=sample_role.id
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with duplicate email
        user2 = User(
            full_name="User 2",
            email="user1@example.com",  # Duplicate
            password_hash="hash",
            role_id=sample_role.id
        )
        db_session.add(user2)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
        
        # Verify only first user exists
        users = db_session.query(User).all()
        assert len(users) == 1
        assert users[0].email == "user1@example.com"


class TestErrorHandling:
    """Integration tests for error handling scenarios."""
    
    def test_not_null_constraint_violation(self, db_session: Session, sample_role: Role):
        """Test handling of NOT NULL constraint violations."""
        # Try to create user without required field
        user = User(
            full_name="Test User",
            # Missing email (required field)
            password_hash="hash",
            role_id=sample_role.id
        )
        db_session.add(user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
        
        db_session.rollback()
    
    def test_invalid_enum_value(self, db_session: Session, sample_project: Project,
                               sample_defect_status: DefectStatus, sample_user: User):
        """Test handling of invalid enum values."""
        # SQLAlchemy will raise an error for invalid enum values
        with pytest.raises((ValueError, DataError)):
            defect = Defect(
                project_id=sample_project.id,
                title="Test",
                priority="invalid_priority",  # Invalid enum value
                status_id=sample_defect_status.id,
                created_by=sample_user.id
            )
            db_session.add(defect)
            db_session.commit()
        
        db_session.rollback()
    
    def test_query_nonexistent_record(self, db_session: Session):
        """Test querying for non-existent records."""
        # Query for non-existent user
        user = db_session.query(User).filter_by(id=99999).first()
        assert user is None
        
        # Query with filter that matches nothing
        users = db_session.query(User).filter_by(email="nonexistent@example.com").all()
        assert len(users) == 0
    
    def test_delete_nonexistent_record(self, db_session: Session):
        """Test attempting to delete a non-existent record."""
        # Create and delete a user
        role = Role(name="Temp", description="Temp role")
        db_session.add(role)
        db_session.commit()
        
        user = User(
            full_name="Temp User",
            email="temp@example.com",
            password_hash="hash",
            role_id=role.id
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        db_session.delete(user)
        db_session.commit()
        
        # Try to query and delete again
        user_to_delete = db_session.query(User).filter_by(id=user_id).first()
        assert user_to_delete is None  # Already deleted


class TestBulkOperations:
    """Integration tests for bulk database operations."""
    
    def test_bulk_insert_defects(self, db_session: Session, sample_project: Project,
                                sample_defect_status: DefectStatus, sample_user: User):
        """Test bulk inserting multiple defects."""
        defects = []
        for i in range(10):
            defect = Defect(
                project_id=sample_project.id,
                title=f"Bulk Defect {i}",
                priority=PriorityEnum.MEDIUM,
                status_id=sample_defect_status.id,
                created_by=sample_user.id
            )
            defects.append(defect)
        
        db_session.add_all(defects)
        db_session.commit()
        
        # Verify all defects were created
        created_defects = db_session.query(Defect).filter(Defect.title.like("Bulk Defect%")).all()
        assert len(created_defects) == 10
    
    def test_bulk_update_defects(self, db_session: Session, sample_project: Project,
                                sample_defect_status: DefectStatus, sample_user: User):
        """Test bulk updating multiple defects."""
        # Create defects
        for i in range(5):
            defect = Defect(
                project_id=sample_project.id,
                title=f"Update Defect {i}",
                priority=PriorityEnum.LOW,
                status_id=sample_defect_status.id,
                created_by=sample_user.id
            )
            db_session.add(defect)
        db_session.commit()
        
        # Bulk update priority
        db_session.query(Defect).filter(
            Defect.title.like("Update Defect%")
        ).update({"priority": PriorityEnum.HIGH})
        db_session.commit()
        
        # Verify updates
        updated_defects = db_session.query(Defect).filter(Defect.title.like("Update Defect%")).all()
        assert all(d.priority == PriorityEnum.HIGH for d in updated_defects)
    
    def test_bulk_delete_comments(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test bulk deleting multiple comments."""
        # Create comments
        for i in range(5):
            comment = Comment(
                defect_id=sample_defect.id,
                user_id=sample_user.id,
                text=f"Delete Comment {i}"
            )
            db_session.add(comment)
        db_session.commit()
        
        # Bulk delete
        db_session.query(Comment).filter(
            Comment.text.like("Delete Comment%")
        ).delete()
        db_session.commit()
        
        # Verify deletion
        remaining_comments = db_session.query(Comment).filter(
            Comment.text.like("Delete Comment%")
        ).all()
        assert len(remaining_comments) == 0
