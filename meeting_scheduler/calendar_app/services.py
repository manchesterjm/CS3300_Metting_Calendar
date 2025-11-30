"""
Service layer for calendar application business logic.

This module implements the Service pattern to separate business logic
from views, following SOFA principles:
- Single Responsibility: Each service class has one clear purpose
- Open/Closed: Services can be extended without modification
- Functional Composition: Complex operations built from simple functions
- Abstraction: Business logic abstracted from presentation layer
"""
import datetime
from typing import List, Set, Tuple
from django.contrib.auth.models import User
from django.db.models import QuerySet
from .models import Unavailability, Group


class TimeSlotService:
    """
    Service for calculating and managing time slots.

    Responsibilities:
    - Generate time slots for a given period
    - Calculate availability based on unavailability records
    - Validate time ranges
    """

    DEFAULT_START_HOUR = 8
    DEFAULT_END_HOUR = 20
    SLOT_DURATION_MINUTES = 30

    @staticmethod
    def generate_time_slots(
        start_time: datetime.time = None,
        end_time: datetime.time = None,
        interval_minutes: int = None
    ) -> List[datetime.time]:
        """
        Generate list of time slots for a period.

        Args:
            start_time: Start time (default: 08:00)
            end_time: End time (default: 20:00)
            interval_minutes: Slot duration (default: 30)

        Returns:
            List of time objects representing each slot
        """
        if start_time is None:
            start_time = datetime.time(TimeSlotService.DEFAULT_START_HOUR, 0)
        if end_time is None:
            end_time = datetime.time(TimeSlotService.DEFAULT_END_HOUR, 0)
        if interval_minutes is None:
            interval_minutes = TimeSlotService.SLOT_DURATION_MINUTES

        slots = []
        current = datetime.datetime.combine(datetime.date.today(), start_time)
        end_dt = datetime.datetime.combine(datetime.date.today(), end_time)

        while current < end_dt:
            slots.append(current.time())
            current += datetime.timedelta(minutes=interval_minutes)

        return slots

    @staticmethod
    def get_taken_slots(
        unavailability_list: QuerySet,
        date: datetime.date
    ) -> Set[datetime.time]:
        """
        Calculate which time slots are taken based on unavailability records.

        Args:
            unavailability_list: QuerySet of Unavailability objects
            date: Date to check slots for

        Returns:
            Set of time objects that are unavailable
        """
        taken = set()

        for unavail in unavailability_list:
            current = datetime.datetime.combine(date, unavail.start_time)
            end = datetime.datetime.combine(date, unavail.end_time)

            while current < end:
                taken.add(current.time())
                current += datetime.timedelta(minutes=TimeSlotService.SLOT_DURATION_MINUTES)

        return taken

    @staticmethod
    def calculate_free_slots(
        user: User,
        date: datetime.date
    ) -> List[str]:
        """
        Calculate free time slots for a user on a specific date.

        Args:
            user: User to check availability for
            date: Date to check

        Returns:
            List of time strings in HH:MM format representing free slots
        """
        # Get all slots
        all_slots = TimeSlotService.generate_time_slots()

        # Get unavailability records
        unavail_list = Unavailability.objects.filter(user=user, date=date)

        # Get taken slots
        taken_slots = TimeSlotService.get_taken_slots(unavail_list, date)

        # Calculate free slots
        free_slots = [
            slot.strftime("%H:%M")
            for slot in all_slots
            if slot not in taken_slots
        ]

        return free_slots


class UnavailabilityService:
    """
    Service for managing unavailability records.

    Responsibilities:
    - Create unavailability records
    - Retrieve user's recent entries
    - Delete entries with validation
    """

    @staticmethod
    def create_unavailability(
        user: User,
        date: datetime.date,
        start_time: datetime.time,
        end_time: datetime.time,
        description: str = ""
    ) -> Unavailability:
        """
        Create a new unavailability record for a user.

        Args:
            user: User the record belongs to
            date: Date of unavailability
            start_time: Start time
            end_time: End time
            description: Optional description

        Returns:
            Created Unavailability object
        """
        return Unavailability.objects.create(
            user=user,
            date=date,
            start_time=start_time,
            end_time=end_time,
            description=description
        )

    @staticmethod
    def get_recent_entries(
        user: User,
        limit: int = 5
    ) -> List[Tuple[int, str]]:
        """
        Get user's most recent unavailability entries formatted for display.

        Args:
            user: User to get entries for
            limit: Maximum number of entries to return

        Returns:
            List of tuples (id, formatted_label)
        """
        entries = Unavailability.objects.filter(user=user).order_by('-id')[:limit]

        return [
            (entry.id, f"{entry.date} from {entry.start_time} to {entry.end_time}")
            for entry in entries
        ]

    @staticmethod
    def delete_entries(
        user: User,
        entry_ids: List[int]
    ) -> int:
        """
        Delete unavailability entries for a user.

        Only deletes entries that belong to the specified user for security.

        Args:
            user: User who owns the entries
            entry_ids: List of entry IDs to delete

        Returns:
            Number of entries deleted
        """
        if not entry_ids:
            return 0

        deleted_count, _ = Unavailability.objects.filter(
            user=user,
            id__in=entry_ids
        ).delete()

        return deleted_count


class GroupCalendarService:
    """
    Service for group calendar operations.

    Responsibilities:
    - Calculate group availability
    - Manage group member access
    - Handle group unavailability records
    """

    @staticmethod
    def calculate_group_free_times(
        group: Group,
        date: datetime.date
    ) -> List[str]:
        """
        Calculate common free times for all group members.

        Args:
            group: Group to check availability for
            date: Date to check

        Returns:
            List of time strings when ALL members are available
        """
        # Get all unique members (owner + members)
        member_ids = set(group.members.values_list('id', flat=True))
        member_ids.add(group.created_by.id)

        # Get all slots
        all_slots = set(TimeSlotService.generate_time_slots())

        # For each member, remove their unavailable slots
        for member_id in member_ids:
            unavail_list = Unavailability.objects.filter(
                user_id=member_id,
                date=date
            )
            taken_slots = TimeSlotService.get_taken_slots(unavail_list, date)
            all_slots -= taken_slots

        # Convert to sorted list of formatted strings
        return sorted([slot.strftime("%H:%M") for slot in all_slots])

    @staticmethod
    def user_can_view_group(user: User, group: Group) -> bool:
        """
        Check if a user has permission to view a group.

        Args:
            user: User to check
            group: Group to check access for

        Returns:
            True if user is owner or member
        """
        return group.is_owner(user) or group.is_member(user)

    @staticmethod
    def user_can_manage_group(user: User, group: Group) -> bool:
        """
        Check if a user can manage a group (add/remove members, delete).

        Args:
            user: User to check
            group: Group to check

        Returns:
            True if user is the owner
        """
        return group.is_owner(user)
