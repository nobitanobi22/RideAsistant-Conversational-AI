from typing import TypedDict, Annotated, Optional, Tuple, Dict, List, Sequence, Any, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState
from pydantic import BaseModel, field_validator, Field
from datetime import datetime
from pydantic import model_validator

class Rider(BaseModel):
    rider_id: Annotated[str, Field(max_length=10, description = "User ID")]
    rider_rating: float = Field(ge=0, default = 5)
    rider_password: Annotated[str, Field(min_length=8, description = "Login Password")]
    prior_cancellations: int = Field(ge=0,default=0)
    total_rides_booked: int = Field(ge=0,default=0)
    cancelation_rate: float = Field(ge=0,le=100,default=0)

    # @field_validator("rider_id")
    # def validate_account_id(cls, value):
    #     if value <= 0:
    #         raise ValueError(f"User ID cannot be negative")
    #     return value

class Driver(BaseModel):
    driver_id: Annotated[str, Field(max_length=10, description = "Driver ID")]
    driver_rating: float = Field(ge=0, default= 5)
    total_rides_accepted: int = Field(ge=0, default=0)
    prior_cancellations: int = Field(ge=0, default=0)
    cancelation_rate: float = Field(ge=0,le=100,default=0)

class CancellationEvent(BaseModel):
    # Who cancelled
    cancelled_by: str = Field(description="Who cancelled the ride - 'driver' or 'rider'")
    
    # Common fields for both driver and rider cancellations
    cancellation_id: str = Field(default="manual_entry")
    rider_id: str
    driver_id: str | None = None  # Made optional since it will be collected during cancellation
    arrived: bool
    distance_from_pin: int | None = None # in meters
    wait_time: int | None = None  # in minutes, if driver arrived
    
    # Rider specific fields
    rider_rating: float
    rider_cancellation_rate: float | None = None
    cancellation_time: int | None = None  # minutes after booking, only for rider cancellations before driver arrival
    
    # Decision field
    decision: str | None = None  # The fee decision from the ML model

class BookingRecord(BaseModel):
    booking_id: str
    rider_id: str
    driver_id: str
    pickup: str
    drop: str
    status: str = "active"  # active, completed, cancelled
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class CancellationRecord(BaseModel):
    cancellation_id: str
    booking_id: str
    rider_id: str
    driver_id: str
    cancelled_by: str  # "rider" or "driver"
    arrived: bool
    distance_from_pin: int | None = None
    wait_time: int | None = None
    rider_rating: float
    rider_cancellation_rate: float | None = None
    cancellation_time: int | None = None  # minutes after booking, for rider cancellations
    decision: str  # fee decision from ML model
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class DriverCancels(BaseModel):
    cancelation_id: str
    rider_id: str
    driver_id: str
    arrived: bool
    distance_from_pin: int | None = None
    wait_time: int | None = None
    rider_rating: float

class RiderCancels(BaseModel):
    cancelation_id: str
    rider_id: str
    driver_id: str
    arrived: bool
    distance_from_pin: int | None = None
    wait_time: int | None = None
    rider_rating: float
    rider_cancelation_rate: float
    cancelation_time: int | None = None

class output(BaseModel):
    tool_call: Literal['book_ride', 'cancel_ride', 'list_bookings', 'answer_query', 'logout']
    pickup: str | None = None
    drop: str | None = None
    booking_id: str | None = None

    @model_validator(mode = "after")
    def check_required_fields(cls, values):
        tool = values.get('tool_call')
        if tool == 'book_ride':
            if not values.get('pickup') or not values.get('drop'):
                raise ValueError("Both 'pickup' and 'drop' must be provided for 'book_ride'")
        elif tool == 'cancel_ride':
            if not values.get('booking_id'):
                raise ValueError("'booking_id' must be provided for 'cancel_ride'")
        return values

class AgentState(MessagesState):
    rider: Rider
    booking_info: BookingRecord | None = None
    cancellation_event: CancellationEvent | None = None
    memory: Dict[str, Any]
    