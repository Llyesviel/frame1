"""
Unit tests for all models in the defect management system.

This module tests model instantiation, field validation, relationships,
cascade behaviors, unique constraints, and indexes.

Requirements: All model requirements
"""

import pytest
from datetime import datetime, date, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Role, User, Project, ProjectStage, DefectStatus, Defect,
    Comment, Attachment, HistoryLog, Report, PriorityEnum, ActionTypeEnum
)


class TestRoleModel:
    """Tests for the Role model."""
    
    def test_role_creation(self, db_session: Session):
        """Test creating a role with valid data."""
        role = Role(name="Manager", description="Manager role")
        db_session.add(role)
        db_session.commit()
        db_session.refresh(role)
        
        assert role.id is not None
        assert role.name == "Manager"
        assert role.description == "Manager role"
    
    def test_role_unique_name_constraint(self, db_session: Session, sample_role: Role):
        """Test that role names must be unique."""
        duplicate_role = Role(name=sample_role.name, description="Duplicate")
        db_session.add(duplicate_role)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_role_relationship_with_users(self, db_session: Session, sample_role: Role, sample_user: User):
        """Test one-to-many relationship between Role and User."""
        assert len(sample_role.users) == 1
        assert sample_role.users[0].id == sample_user.id


class TestUserModel:
    """Tests for the User model."""
    
    def test_user_creation(self, db_session: Session, sample_role: Role):
        """Test creating a user with valid data."""
        user = User(
            full_name="Jane Smith",
            email="jane.smith@example.com",
            password_hash="hashed_password",
            role_id=sample_role.id,
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.full_name == "Jane Smith"
        assert user.email == "jane.smith@example.com"
        assert user.password_hash == "hashed_password"
        assert user.role_id == sample_role.id
        assert user.is_active is True
        assert user.created_at is not None
        assert isinstance(user.created_at, datetime)
    
    def test_user_unique_email_constraint(self, db_session: Session, sample_user: User, sample_role: Role):
        """Test that user emails must be unique."""
        duplicate_user = User(
            full_name="Another User",
            email=sample_user.email,
            password_hash="password",
            role_id=sample_role.id
        )
        db_session.add(duplicate_user)
        
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_user_role_relationship(self, db_session: Session, sample_user: User, sample_role: Role):
        """Test many-to-one relationship between User and Role."""
        assert sample_user.role.id == sample_role.id
        assert sample_user.role.name == sample_role.name


class TestProjectModel:
    """Tests for the Project model."""
    
    def test_project_creation(self, db_session: Session, sample_user: User):
        """Test creating a project with valid data."""
        project = Project(
            name="New Building",
            description="Construction of new building",
            manager_id=sample_user.id,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31)
        )
        db_session.add(project)
        db_session.commit()
        db_session.refresh(project)
        
        assert project.id is not None
        assert project.name == "New Building"
        assert project.description == "Construction of new building"
        assert project.manager_id == sample_user.id
        assert project.start_date == date(2024, 1, 1)
        assert project.end_date == date(2024, 12, 31)
        assert project.created_at is not None
    
    def test_project_manager_relationship(self, db_session: Session, sample_project: Project, sample_user: User):
        """Test many-to-one relationship between Project and User (manager)."""
        assert sample_project.manager.id == sample_user.id
        assert sample_project.manager.email == sample_user.email
    
    def test_project_stages_relationship(self, db_session: Session, sample_project: Project):
        """Test one-to-many relationship between Project and ProjectStage."""
        stage = ProjectStage(
            project_id=sample_project.id,
            name="Foundation",
            description="Foundation work"
        )
        db_session.add(stage)
        db_session.commit()
        db_session.refresh(sample_project)
        
        assert len(sample_project.stages) == 1
        assert sample_project.stages[0].name == "Foundation"


class TestProjectStageModel:
    """Tests for the ProjectStage model."""
    
    def test_project_stage_creation(self, db_session: Session, sample_project: Project):
        """Test creating a project stage with valid data."""
        stage = ProjectStage(
            project_id=sample_project.id,
            name="Framing",
            description="Framing work",
            start_date=date(2024, 2, 1),
            end_date=date(2024, 4, 30)
        )
        db_session.add(stage)
        db_session.commit()
        db_session.refresh(stage)
        
        assert stage.id is not None
        assert stage.project_id == sample_project.id
        assert stage.name == "Framing"
        assert stage.description == "Framing work"
        assert stage.start_date == date(2024, 2, 1)
        assert stage.end_date == date(2024, 4, 30)
    
    def test_project_stage_project_relationship(self, db_session: Session, sample_project: Project):
        """Test many-to-one relationship between ProjectStage and Project."""
        stage = ProjectStage(
            project_id=sample_project.id,
            name="Finishing",
            description="Finishing work"
        )
        db_session.add(stage)
        db_session.commit()
        db_session.refresh(stage)
        
        assert stage.project.id == sample_project.id
        assert stage.project.name == sample_project.name
    
    def test_project_stage_cascade_delete(self, db_session: Session, sample_project: Project):
        """Test cascade delete behavior when project is deleted."""
        stage = ProjectStage(
            project_id=sample_project.id,
            name="Electrical",
            description="Electrical work"
        )
        db_session.add(stage)
        db_session.commit()
        stage_id = stage.id
        
        # Delete the project
        db_session.delete(sample_project)
        db_session.commit()
        
        # Verify stage is also deleted
        deleted_stage = db_session.query(ProjectStage).filter_by(id=stage_id).first()
        assert deleted_stage is None


class TestDefectStatusModel:
    """Tests for the DefectStatus model."""
    
    def test_defect_status_creation(self, db_session: Session):
        """Test creating a defect status with valid data."""
        status = DefectStatus(name="In Progress", description="Work in progress")
        db_session.add(status)
        db_session.commit()
        db_session.refresh(status)
        
        assert status.id is not None
        assert status.name == "In Progress"
        assert status.description == "Work in progress"
    
    def test_defect_status_unique_name_constraint(self, db_session: Session, sample_defect_status: DefectStatus):
        """Test that defect status names must be unique."""
        duplicate_status = DefectStatus(name=sample_defect_status.name, description="Duplicate")
        db_session.add(duplicate_status)
        
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestDefectModel:
    """Tests for the Defect model."""
    
    def test_defect_creation(self, db_session: Session, sample_project: Project, 
                            sample_defect_status: DefectStatus, sample_user: User):
        """Test creating a defect with valid data."""
        defect = Defect(
            project_id=sample_project.id,
            title="Cracked wall",
            description="Wall has visible cracks",
            priority=PriorityEnum.CRITICAL,
            status_id=sample_defect_status.id,
            created_by=sample_user.id,
            assigned_to=sample_user.id,
            due_date=date(2024, 6, 30)
        )
        db_session.add(defect)
        db_session.commit()
        db_session.refresh(defect)
        
        assert defect.id is not None
        assert defect.project_id == sample_project.id
        assert defect.title == "Cracked wall"
        assert defect.description == "Wall has visible cracks"
        assert defect.priority == PriorityEnum.CRITICAL
        assert defect.status_id == sample_defect_status.id
        assert defect.created_by == sample_user.id
        assert defect.assigned_to == sample_user.id
        assert defect.due_date == date(2024, 6, 30)
        assert defect.created_at is not None
    
    def test_defect_priority_enum(self, db_session: Session, sample_project: Project,
                                  sample_defect_status: DefectStatus, sample_user: User):
        """Test that defect priority uses PriorityEnum."""
        for priority in [PriorityEnum.LOW, PriorityEnum.MEDIUM, PriorityEnum.HIGH, PriorityEnum.CRITICAL]:
            defect = Defect(
                project_id=sample_project.id,
                title=f"Defect with {priority.value} priority",
                priority=priority,
                status_id=sample_defect_status.id,
                created_by=sample_user.id
            )
            db_session.add(defect)
            db_session.commit()
            db_session.refresh(defect)
            
            assert defect.priority == priority
            db_session.delete(defect)
            db_session.commit()
    
    def test_defect_relationships(self, db_session: Session, sample_defect: Defect,
                                 sample_project: Project, sample_defect_status: DefectStatus,
                                 sample_user: User):
        """Test relationships between Defect and other models."""
        assert sample_defect.project.id == sample_project.id
        assert sample_defect.status.id == sample_defect_status.id
        assert sample_defect.creator.id == sample_user.id
    
    def test_defect_with_stage(self, db_session: Session, sample_project: Project,
                              sample_defect_status: DefectStatus, sample_user: User):
        """Test defect with project stage relationship."""
        stage = ProjectStage(
            project_id=sample_project.id,
            name="Foundation",
            description="Foundation stage"
        )
        db_session.add(stage)
        db_session.commit()
        db_session.refresh(stage)
        
        defect = Defect(
            project_id=sample_project.id,
            stage_id=stage.id,
            title="Foundation issue",
            priority=PriorityEnum.HIGH,
            status_id=sample_defect_status.id,
            created_by=sample_user.id
        )
        db_session.add(defect)
        db_session.commit()
        db_session.refresh(defect)
        
        assert defect.stage.id == stage.id
        assert defect.stage.name == "Foundation"


class TestCommentModel:
    """Tests for the Comment model."""
    
    def test_comment_creation(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test creating a comment with valid data."""
        comment = Comment(
            defect_id=sample_defect.id,
            user_id=sample_user.id,
            text="This is a test comment"
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        
        assert comment.id is not None
        assert comment.defect_id == sample_defect.id
        assert comment.user_id == sample_user.id
        assert comment.text == "This is a test comment"
        assert comment.created_at is not None
    
    def test_comment_relationships(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test relationships between Comment and other models."""
        comment = Comment(
            defect_id=sample_defect.id,
            user_id=sample_user.id,
            text="Test comment"
        )
        db_session.add(comment)
        db_session.commit()
        db_session.refresh(comment)
        
        assert comment.defect.id == sample_defect.id
        assert comment.user.id == sample_user.id
    
    def test_comment_cascade_delete(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test cascade delete behavior when defect is deleted."""
        comment = Comment(
            defect_id=sample_defect.id,
            user_id=sample_user.id,
            text="Comment to be deleted"
        )
        db_session.add(comment)
        db_session.commit()
        comment_id = comment.id
        
        # Delete the defect
        db_session.delete(sample_defect)
        db_session.commit()
        
        # Verify comment is also deleted
        deleted_comment = db_session.query(Comment).filter_by(id=comment_id).first()
        assert deleted_comment is None


class TestAttachmentModel:
    """Tests for the Attachment model."""
    
    def test_attachment_creation(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test creating an attachment with valid data."""
        attachment = Attachment(
            defect_id=sample_defect.id,
            uploaded_by=sample_user.id,
            file_name="photo.jpg",
            file_path="/uploads/photo.jpg",
            is_deleted=False
        )
        db_session.add(attachment)
        db_session.commit()
        db_session.refresh(attachment)
        
        assert attachment.id is not None
        assert attachment.defect_id == sample_defect.id
        assert attachment.uploaded_by == sample_user.id
        assert attachment.file_name == "photo.jpg"
        assert attachment.file_path == "/uploads/photo.jpg"
        assert attachment.is_deleted is False
        assert attachment.uploaded_at is not None
    
    def test_attachment_soft_delete(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test soft delete functionality for attachments."""
        attachment = Attachment(
            defect_id=sample_defect.id,
            uploaded_by=sample_user.id,
            file_name="document.pdf",
            file_path="/uploads/document.pdf"
        )
        db_session.add(attachment)
        db_session.commit()
        db_session.refresh(attachment)
        
        # Soft delete
        attachment.is_deleted = True
        db_session.commit()
        db_session.refresh(attachment)
        
        assert attachment.is_deleted is True
        # Attachment still exists in database
        assert db_session.query(Attachment).filter_by(id=attachment.id).first() is not None
    
    def test_attachment_relationships(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test relationships between Attachment and other models."""
        attachment = Attachment(
            defect_id=sample_defect.id,
            uploaded_by=sample_user.id,
            file_name="image.png",
            file_path="/uploads/image.png"
        )
        db_session.add(attachment)
        db_session.commit()
        db_session.refresh(attachment)
        
        assert attachment.defect.id == sample_defect.id
        assert attachment.uploader.id == sample_user.id
    
    def test_attachment_cascade_delete(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test cascade delete behavior when defect is deleted."""
        attachment = Attachment(
            defect_id=sample_defect.id,
            uploaded_by=sample_user.id,
            file_name="file.txt",
            file_path="/uploads/file.txt"
        )
        db_session.add(attachment)
        db_session.commit()
        attachment_id = attachment.id
        
        # Delete the defect
        db_session.delete(sample_defect)
        db_session.commit()
        
        # Verify attachment is also deleted
        deleted_attachment = db_session.query(Attachment).filter_by(id=attachment_id).first()
        assert deleted_attachment is None


class TestHistoryLogModel:
    """Tests for the HistoryLog model."""
    
    def test_history_log_creation(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test creating a history log with valid data."""
        history = HistoryLog(
            defect_id=sample_defect.id,
            user_id=sample_user.id,
            action_type=ActionTypeEnum.CREATE,
            old_value=None,
            new_value="Defect created"
        )
        db_session.add(history)
        db_session.commit()
        db_session.refresh(history)
        
        assert history.id is not None
        assert history.defect_id == sample_defect.id
        assert history.user_id == sample_user.id
        assert history.action_type == ActionTypeEnum.CREATE
        assert history.old_value is None
        assert history.new_value == "Defect created"
        assert history.timestamp is not None
    
    def test_history_log_action_types(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test all action types for history log."""
        action_types = [
            ActionTypeEnum.CREATE,
            ActionTypeEnum.UPDATE,
            ActionTypeEnum.STATUS_CHANGE,
            ActionTypeEnum.COMMENT_ADDED
        ]
        
        for action_type in action_types:
            history = HistoryLog(
                defect_id=sample_defect.id,
                user_id=sample_user.id,
                action_type=action_type,
                old_value="old",
                new_value="new"
            )
            db_session.add(history)
            db_session.commit()
            db_session.refresh(history)
            
            assert history.action_type == action_type
            db_session.delete(history)
            db_session.commit()
    
    def test_history_log_relationships(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test relationships between HistoryLog and other models."""
        history = HistoryLog(
            defect_id=sample_defect.id,
            user_id=sample_user.id,
            action_type=ActionTypeEnum.UPDATE,
            old_value="old status",
            new_value="new status"
        )
        db_session.add(history)
        db_session.commit()
        db_session.refresh(history)
        
        assert history.defect.id == sample_defect.id
        assert history.user.id == sample_user.id
    
    def test_history_log_cascade_delete(self, db_session: Session, sample_defect: Defect, sample_user: User):
        """Test cascade delete behavior when defect is deleted."""
        history = HistoryLog(
            defect_id=sample_defect.id,
            user_id=sample_user.id,
            action_type=ActionTypeEnum.STATUS_CHANGE,
            old_value="New",
            new_value="In Progress"
        )
        db_session.add(history)
        db_session.commit()
        history_id = history.id
        
        # Delete the defect
        db_session.delete(sample_defect)
        db_session.commit()
        
        # Verify history log is also deleted
        deleted_history = db_session.query(HistoryLog).filter_by(id=history_id).first()
        assert deleted_history is None


class TestReportModel:
    """Tests for the Report model."""
    
    def test_report_creation(self, db_session: Session, sample_project: Project, sample_user: User):
        """Test creating a report with valid data."""
        report = Report(
            project_id=sample_project.id,
            report_type="by status",
            generated_by=sample_user.id,
            file_path="/reports/report_001.csv"
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)
        
        assert report.id is not None
        assert report.project_id == sample_project.id
        assert report.report_type == "by status"
        assert report.generated_by == sample_user.id
        assert report.file_path == "/reports/report_001.csv"
        assert report.created_at is not None
    
    def test_report_relationships(self, db_session: Session, sample_project: Project, sample_user: User):
        """Test relationships between Report and other models."""
        report = Report(
            project_id=sample_project.id,
            report_type="by assignee",
            generated_by=sample_user.id,
            file_path="/reports/report_002.xlsx"
        )
        db_session.add(report)
        db_session.commit()
        db_session.refresh(report)
        
        assert report.project.id == sample_project.id
        assert report.generator.id == sample_user.id
    
    def test_multiple_report_types(self, db_session: Session, sample_project: Project, sample_user: User):
        """Test creating reports with different types."""
        report_types = ["by status", "by assignee", "by priority", "summary"]
        
        for report_type in report_types:
            report = Report(
                project_id=sample_project.id,
                report_type=report_type,
                generated_by=sample_user.id,
                file_path=f"/reports/{report_type.replace(' ', '_')}.csv"
            )
            db_session.add(report)
            db_session.commit()
            db_session.refresh(report)
            
            assert report.report_type == report_type


class TestModelIntegration:
    """Integration tests for complex model interactions."""
    
    def test_complete_defect_workflow(self, db_session: Session, sample_role: Role):
        """Test a complete workflow from user creation to defect with all related entities."""
        # Create users
        manager = User(
            full_name="Project Manager",
            email="manager@example.com",
            password_hash="hash1",
            role_id=sample_role.id
        )
        engineer = User(
            full_name="Engineer",
            email="engineer@example.com",
            password_hash="hash2",
            role_id=sample_role.id
        )
        db_session.add_all([manager, engineer])
        db_session.commit()
        
        # Create project
        project = Project(
            name="Building A",
            description="Main building",
            manager_id=manager.id
        )
        db_session.add(project)
        db_session.commit()
        
        # Create project stage
        stage = ProjectStage(
            project_id=project.id,
            name="Foundation",
            description="Foundation work"
        )
        db_session.add(stage)
        db_session.commit()
        
        # Create defect status
        status = DefectStatus(name="New", description="New defect")
        db_session.add(status)
        db_session.commit()
        
        # Create defect
        defect = Defect(
            project_id=project.id,
            stage_id=stage.id,
            title="Foundation crack",
            description="Crack in foundation",
            priority=PriorityEnum.CRITICAL,
            status_id=status.id,
            created_by=engineer.id,
            assigned_to=engineer.id
        )
        db_session.add(defect)
        db_session.commit()
        
        # Add comment
        comment = Comment(
            defect_id=defect.id,
            user_id=manager.id,
            text="Please fix urgently"
        )
        db_session.add(comment)
        db_session.commit()
        
        # Add attachment
        attachment = Attachment(
            defect_id=defect.id,
            uploaded_by=engineer.id,
            file_name="crack_photo.jpg",
            file_path="/uploads/crack_photo.jpg"
        )
        db_session.add(attachment)
        db_session.commit()
        
        # Add history log
        history = HistoryLog(
            defect_id=defect.id,
            user_id=engineer.id,
            action_type=ActionTypeEnum.CREATE,
            new_value="Defect created"
        )
        db_session.add(history)
        db_session.commit()
        
        # Create report
        report = Report(
            project_id=project.id,
            report_type="by status",
            generated_by=manager.id,
            file_path="/reports/status_report.csv"
        )
        db_session.add(report)
        db_session.commit()
        
        # Verify all relationships
        db_session.refresh(defect)
        assert len(defect.comments) == 1
        assert len(defect.attachments) == 1
        assert len(defect.history_logs) == 1
        assert defect.project.name == "Building A"
        assert defect.stage.name == "Foundation"
        assert defect.creator.email == "engineer@example.com"
        assert defect.assignee.email == "engineer@example.com"
        
        db_session.refresh(project)
        assert len(project.defects) == 1
        assert len(project.stages) == 1
        assert len(project.reports) == 1
