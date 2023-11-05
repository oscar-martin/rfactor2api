import model
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
import math

unknown = "desconocido"

def session_to_string(type):
    return {
        0: "TestDay",
        1: "Practice1",
        2: "Practice2",
        3: "Practice3",
        4: "Practice4",
        5: "Qual1",
        5: "Qual2",
        7: "Qual3",
        8: "Qual4",
        9: "WarmUp",
        10: "Race1",
        11: "Race2",
        12: "Race3",
        13: "Race4",
    }.get(type, unknown)

def finish_status_to_string(type):
    return {
        0: "",
        1: "Finished",
        2: "DNF",
        3: "Disqualified",
    }.get(type, unknown)

class Player(BaseModel):
    driveName: bytes = unknown
    vehicleName: bytes = unknown
    vehicleClass: bytes = unknown
    totalLaps: int = 0
    place: int = 0 # 1-based position
    inPits: bool = True
    numPitstops: int = 0
    finishStatus: str = unknown
    bestSector1: Optional[float] = None
    bestSector2: Optional[float] = None
    bestSector3: Optional[float] = None
    bestLapTime: Optional[float] = None
    lastSector1: Optional[float] = None
    lastSector2: Optional[float] = None
    lastSector3: Optional[float] = None
    lastLapTime: Optional[float] = None
    currentSector1: Optional[float] = None  # current sector 1 if valid
    currentSector2: Optional[float] = None  # current sector 2 if valid
    currentLapTime: Optional[float] = None
    speed: Optional[float] = None

    def __init__(self, vehicle: model.rF2VehicleScoring, currentET: float):
        super().__init__()
        self.driveName = vehicle.mDriverName
        self.vehicleName = vehicle.mVehicleName
        self.vehicleClass = vehicle.mVehicleClass
        self.totalLaps = vehicle.mTotalLaps
        self.place = vehicle.mPlace
        self.inPits = vehicle.mInPits
        self.numPitstops = vehicle.mNumPitstops
        self.finishStatus = finish_status_to_string(vehicle.mFinishStatus)
        self.bestSector1 = vehicle.mBestLapSector1
        self.bestSector2 = vehicle.mBestLapSector2 - vehicle.mBestLapSector1
        self.bestSector3 = vehicle.mBestLapTime - vehicle.mBestLapSector2
        self.bestLapTime = vehicle.mBestLapTime
        self.lastSector1 = vehicle.mLastSector1
        self.lastSector2 = vehicle.mLastSector2 - vehicle.mLastSector1
        self.lastSector3 = vehicle.mLastLapTime - vehicle.mLastSector2
        self.lastLapTime = vehicle.mLastLapTime
        self.currentSector1 = vehicle.mCurSector1
        self.currentSector2 = vehicle.mCurSector2
        self.currentLapTime = currentET - vehicle.mLapStartET
        mps = math.sqrt(math.pow(vehicle.mLocalVel.x, 2) +
                  math.pow(vehicle.mLocalVel.y, 2) +
                  math.pow(vehicle.mLocalVel.z, 2))
        self.speed = mps*3.6

class Session(BaseModel):
    active: bool = False
    trackName: bytes = unknown
    sessionName: str = unknown
    lapDistance: float = 0.0
    maxLaps: int = 0
    raining: float = 0.0
    ambientTemp: float = 0.0
    trackTemp: float = 0.0
    minPathWetness: float = 0.0
    maxPathWetness: float = 0.0
    players: List[Player] = []

    def __init__(self, scoring: model.rF2Scoring, active: bool):
        super().__init__()
        self.active = active
        self.trackName = scoring.mScoringInfo.mTrackName
        self.sessionName = session_to_string(scoring.mScoringInfo.mSession)
        self.lapDistance = scoring.mScoringInfo.mLapDist
        self.maxLaps = scoring.mScoringInfo.mMaxLaps
        self.raining = scoring.mScoringInfo.mRaining
        self.ambientTemp = scoring.mScoringInfo.mAmbientTemp
        self.trackTemp = scoring.mScoringInfo.mTrackTemp
        self.minPathWetness = scoring.mScoringInfo.mMinPathWetness
        self.maxPathWetness = scoring.mScoringInfo.mMaxPathWetness
    
        for i in range(scoring.mScoringInfo.mNumVehicles):
            self.players.append(Player(scoring.mVehicles[i], scoring.mScoringInfo.mCurrentET))

