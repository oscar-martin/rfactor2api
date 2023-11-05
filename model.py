from pydantic import BaseModel
from typing import List, Any
from enum import Enum
from typing import Optional
from ctypes import Array, Structure, Union, _Pointer, _SimpleCData
from json import JSONEncoder
import json

def Cbytestring2Python(bytestring):
    """
    C string to Python string
    """
    try:
        return bytes(bytestring).partition(b'\0')[0].decode('utf_8').rstrip()
    except BaseException:
        pass
    try:    # Codepage 1252 includes Scandinavian characters
        return bytes(bytestring).partition(b'\0')[0].decode('cp1252').rstrip()
    except BaseException:
        pass
    try:    # OK, struggling, just ignore errors
        return bytes(bytestring).partition(b'\0')[
            0].decode('utf_8', 'ignore').rstrip()
    except Exception as e:
        print('Trouble decoding a string')
        print(e)

class CDataJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (Array, list)):
            return [self.default(e) for e in obj]

        if isinstance(obj, _Pointer):
            return self.default(obj.contents) if obj else None

        if isinstance(obj, _SimpleCData):
            return self.default(obj.value)

        if isinstance(obj, (bool, int, float, str)):
            return obj

        if obj is None:
            return obj

        if isinstance(obj, (Structure, Union)):
            result = {}
            anonymous = getattr(obj, '_anonymous_', [])

            for key, *_ in getattr(obj, '_fields_', []):
                value = getattr(obj, key)

                # private fields don't encode
                if key.startswith('_'):
                    continue

                if key in anonymous:
                    result.update(self.default(value))
                else:
                    result[key] = self.default(value)

            return result
        if isinstance(obj, bytes):
            return Cbytestring2Python(obj)

        return JSONEncoder.default(self, obj)
    
class rF2GamePhase(Enum):
        Garage = 0
        WarmUp = 1
        GridWalk = 2
        Formation = 3
        Countdown = 4
        GreenFlag = 5
        FullCourseYellow = 6
        SessionStopped = 7
        SessionOver = 8
        PausedOrHeartbeat = 9

class rF2YellowFlagState(Enum):
        Invalid = -1
        NoFlag = 0
        Pending = 1
        PitClosed = 2
        PitLeadLap = 3
        PitOpen = 4
        LastLap = 5
        Resume = 6
        RaceHalt = 7

class rF2SurfaceType(Enum):
        Dry = 0
        Wet = 1
        Grass = 2
        Dirt = 3
        Gravel = 4
        Kerb = 5
        Special = 6

class rF2Sector(Enum):
        Sector3 = 0
        Sector1 = 1
        Sector2 = 2

class rF2FinishStatus(Enum):
        _None = 0
        Finished = 1
        Dnf = 2
        Dq = 3

class rF2Control(Enum):
        Nobody = -1
        Player = 0
        AI = 1
        Remote = 2
        Replay = 3

class rF2WheelIndex(Enum):
        FrontLeft = 0
        FrontRight = 1
        RearLeft = 2
        RearRight = 3

class rF2PitState(Enum):
        _None = 0
        Request = 1
        Entering = 2
        Stopped = 3
        Exiting = 4

class rF2PrimaryFlag(Enum):
        Green = 0
        Blue = 6

class rF2CountLapFlag(Enum):
        DoNotCountLap = 0
        CountLapButNotTime = 1
        CountLapAndTime = 2

class rF2RearFlapLegalStatus(Enum):
        Disallowed = 0
        DetectedButNotAllowedYet = 1
        Alllowed = 2

class rF2IgnitionStarterStatus(Enum):
        Off = 0
        Ignition = 1
        IgnitionAndStarter = 2

class rF2SafetyCarInstruction(Enum):
        NoChange = 0
        GoActive = 1
        HeadForPits = 2


class rF2Vec3(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None


class rF2Wheel(BaseModel):
    mSuspensionDeflection: Optional[float] = None  # meters
    mRideHeight: Optional[float] = None  # meters
    mSuspForce: Optional[float] = None  # pushrod load in Newtons
    mBrakeTemp: Optional[float] = None  # Celsius
    mBrakePressure: Optional[float] = None  # currently 0.0-1.0, depending on driver input and brake balance; will convert to true brake pressure (kPa) in the future

    mRotation: Optional[float] = None  # radians/sec
    mLateralPatchVel: Optional[float] = None  # lateral velocity at the contact patch
    mLongitudinalPatchVel: Optional[float] = None  # longitudinal velocity at the contact patch
    mLateralGroundVel: Optional[float] = None  # lateral velocity at the contact patch
    mLongitudinalGroundVel: Optional[float] = None  # longitudinal velocity at the contact patch
    mCamber: Optional[float] = None  # radians (positive is left for left-side wheels, right for right-side wheels)
    mLateralForce: Optional[float] = None  # Newtons
    mLongitudinalForce: Optional[float] = None  # Newtons
    mTireLoad: Optional[float] = None  # Newtons

    mGripFract: Optional[float] = None  # an approximation of what fraction of the contact patch is sliding
    mPressure: Optional[float] = None  # kPa (tire pressure)
    mTemperature: Optional[List[float]] = None  # Kelvin (subtract 273.15 to get Celsius), left/center/right (not to be confused with inside/center/outside!)
    mWear: Optional[float] = None  # wear (0.0-1.0, fraction of maximum) ... this is not necessarily proportional with grip loss
    mTerrainName: Optional[bytes] = None  # the material prefixes from the TDF file
    mSurfaceType: Optional[int] = None  # 0=dry, 1=wet, 2=grass, 3=dirt, 4=gravel, 5=rumblestrip, 6=special
    mFlat: Optional[bool] = None  # whether the tire is flat
    mDetached: Optional[bool] = None  # whether the wheel is detached
    mStaticUndeflectedRadius: Optional[int] = None  # tire radius in centimeters

    mVerticalTireDeflection: Optional[float] = None  # how much the tire is deflected from its (speed-sensitive) radius
    mWheelYLocation: Optional[float] = None  # wheel's y location relative to the vehicle y location
    mToe: Optional[float] = None  # current toe angle w.r.t. the vehicle

    mTireCarcassTemperature: Optional[float] = None  # rough average of temperature samples from the carcass (Kelvin)
    mTireInnerLayerTemperature: Optional[List[float]] = None  # rough average of temperature samples from the innermost layer of rubber (before carcass) (Kelvin)

    mExpansion: Optional[List[int]] = None  # for future use

class rF2VehicleTelemetry(BaseModel):
    mID: Optional[int] = None  # slot ID (note that it can be re-used in multiplayer after someone leaves)
    mDeltaTime: Optional[float] = None  # time since the last update (seconds)
    mElapsedTime: Optional[float] = None  # game session time
    mLapNumber: Optional[int] = None  # current lap number
    mLapStartET: Optional[float] = None  # time this lap was started
    mVehicleName: Optional[bytes] = None  # current vehicle name
    mTrackName: Optional[bytes] = None  # current track name

    # Position and derivatives
    mPos: Optional[rF2Vec3] = None  # world position in meters
    mLocalVel: Optional[rF2Vec3] = None  # velocity (meters/sec) in local vehicle coordinates
    mLocalAccel: Optional[rF2Vec3] = None  # acceleration (meters/sec^2) in local vehicle coordinates

    # Orientation and derivatives
    mOri: Optional[List[rF2Vec3]] = None  # rows of orientation matrix
    mLocalRot: Optional[rF2Vec3] = None  # rotation (radians/sec) in local vehicle coordinates
    mLocalRotAccel: Optional[rF2Vec3] = None  # rotational acceleration (radians/sec^2) in local vehicle coordinates

    # Vehicle status
    mGear: Optional[int] = None  # -1=reverse, 0=neutral, 1+=forward gears
    mEngineRPM: Optional[float] = None  # engine RPM
    mEngineWaterTemp: Optional[float] = None  # Celsius
    mEngineOilTemp: Optional[float] = None  # Celsius
    mClutchRPM: Optional[float] = None  # clutch RPM

    # Driver input
    mUnfilteredThrottle: Optional[float] = None  # ranges  0.0-1.0
    mUnfilteredBrake: Optional[float] = None  # ranges  0.0-1.0
    mUnfilteredSteering: Optional[float] = None  # ranges -1.0-1.0 (left to right)
    mUnfilteredClutch: Optional[float] = None  # ranges  0.0-1.0

    # Filtered input
    mFilteredThrottle: Optional[float] = None  # ranges  0.0-1.0
    mFilteredBrake: Optional[float] = None  # ranges  0.0-1.0
    mFilteredSteering: Optional[float] = None  # ranges -1.0-1.0 (left to right)
    mFilteredClutch: Optional[float] = None  # ranges  0.0-1.0

    # Misc
    mSteeringShaftTorque: Optional[float] = None  # torque around the steering shaft
    mFront3rdDeflection: Optional[float] = None  # deflection at front 3rd spring
    mRear3rdDeflection: Optional[float] = None  # deflection at rear 3rd spring

    # Aerodynamics
    mFrontWingHeight: Optional[float] = None  # front wing height
    mFrontRideHeight: Optional[float] = None  # front ride height
    mRearRideHeight: Optional[float] = None  # rear ride height
    mDrag: Optional[float] = None  # drag
    mFrontDownforce: Optional[float] = None  # front downforce
    mRearDownforce: Optional[float] = None  # rear downforce

    # State/damage info
    mFuel: Optional[float] = None  # amount of fuel (liters)
    mEngineMaxRPM: Optional[float] = None  # rev limit
    mScheduledStops: Optional[int] = None  # number of scheduled pitstops
    mOverheating: Optional[bool] = None  # whether overheating icon is shown
    mDetached: Optional[bool] = None  # whether any parts (besides wheels) have been detached
    mHeadlights: Optional[bool] = None  # whether headlights are on
    mDentSeverity: Optional[List[int]] = None  # dent severity at 8 locations around the car (0=none, 1=some, 2=more)
    mLastImpactET: Optional[float] = None  # time of the last impact
    mLastImpactMagnitude: Optional[float] = None  # magnitude of the last impact
    mLastImpactPos: Optional[rF2Vec3] = None  # location of the last impact

    # Expanded
    mEngineTorque: Optional[float] = None  # current engine torque (including additive torque)
    mCurrentSector: Optional[int] = None  # the current sector with the pitlane stored in the sign bit
    mSpeedLimiter: Optional[int] = None  # whether the speed limiter is on
    mMaxGears: Optional[int] = None  # maximum forward gears
    mFrontTireCompoundIndex: Optional[int] = None  # index within brand
    mRearTireCompoundIndex: Optional[int] = None  # index within brand
    mFuelCapacity: Optional[float] = None  # capacity in liters
    mFrontFlapActivated: Optional[int] = None  # whether the front flap is activated
    mRearFlapActivated: Optional[int] = None  # whether the rear flap is activated
    mRearFlapLegalStatus: Optional[int] = None  # 0=disallowed, 1=criteria detected but not allowed yet, 2=allowed
    mIgnitionStarter: Optional[int] = None  # 0=off 1=ignition 2=ignition+starter
    mFrontTireCompoundName: Optional[bytes] = None  # name of front tire compound
    mRearTireCompoundName: Optional[bytes] = None  # name of rear tire compound
    mSpeedLimiterAvailable: Optional[int] = None  # whether the speed limiter is available
    mAntiStallActivated: Optional[int] = None  # whether (hard) anti-stall is activated
    mUnused: Optional[List[int]] = None
    mVisualSteeringWheelRange: Optional[float] = None  # the visual steering wheel range
    mRearBrakeBias: Optional[float] = None  # fraction of brakes on the rear
    mTurboBoostPressure: Optional[float] = None  # current turbo boost pressure if available
    mPhysicsToGraphicsOffset: Optional[List[float]] = None  # offset from static CG to graphical center
    mPhysicalSteeringWheelRange: Optional[float] = None  # the physical steering wheel range
    mBatteryChargeFraction: Optional[float] = None  # Battery charge as a fraction [0.0-1.0]
    mElectricBoostMotorTorque: Optional[float] = None  # current torque of the boost motor
    mElectricBoostMotorRPM: Optional[float] = None  # current rpm of the boost motor
    mElectricBoostMotorTemperature: Optional[float] = None  # current temperature of the boost motor
    mElectricBoostWaterTemperature: Optional[float] = None  # current water temperature of the boost motor cooler if present (0 otherwise)
    mElectricBoostMotorState: Optional[int] = None  # 0=unavailable 1=inactive, 2=propulsion, 3=regeneration
    mExpansion: Optional[List[int]] = None  # for future use (note that the slot ID has been moved to mID above)
    mWheels: Optional[List[rF2Wheel]] = None  # wheel info (front left, front right, rear left, rear right)

class rF2ScoringInfo(BaseModel):
    mTrackName: Optional[bytes] = None # current track name
    mSession: Optional[int] = None # current session (0=testday 1-4=practice 5-8=qual 9=warmup 10-13=race)
    mCurrentET: Optional[float] = None # current time
    mEndET: Optional[float] = None  # ending time
    mMaxLaps: Optional[int] = None  # maximum laps
    mLapDist: Optional[float] = None  # distance around the track
    pointer1: Optional[List[int]] = None

    mNumVehicles: Optional[int] = None  # current number of vehicles
    mGamePhase: Optional[int] = None  # Game phases
    mYellowFlagState: Optional[str] = None  # Yellow flag states (applies to full-course only)
    mSectorFlag: Optional[List[int]] = None  # whether there are any local yellows at the moment in each sector
    mStartLight: Optional[int] = None  # start light frame
    mNumRedLights: Optional[int] = None  # number of red lights in the start sequence
    mInRealtime: Optional[bool] = None  # in realtime as opposed to at the monitor
    mPlayerName: Optional[bytes] = None  # player name (including possible multiplayer override)
    mPlrFileName: Optional[bytes] = None  # may be encoded to be a legal filename

    # Weather
    mDarkCloud: Optional[float] = None  # cloud darkness
    mRaining: Optional[float] = None  # raining severity
    mAmbientTemp: Optional[float] = None  # temperature (Celsius)
    mTrackTemp: Optional[float] = None  # temperature (Celsius)
    mWind: Optional[rF2Vec3] = None  # wind speed
    mMinPathWetness: Optional[float] = None  # minimum wetness on the main path
    mMaxPathWetness: Optional[float] = None  # maximum wetness on the main path

    # Multiplayer
    mGameMode: Optional[int] = None  # 1 = server, 2 = client, 3 = server and client
    mIsPasswordProtected: Optional[bool] = None  # is the server password protected
    mServerPort: Optional[int] = None  # the port of the server (if on a server)
    mServerPublicIP: Optional[int] = None  # the public IP address of the server (if on a server)
    mMaxPlayers: Optional[int] = None  # maximum number of vehicles that can be in the session
    mServerName: Optional[bytes] = None  # name of the server
    mStartET: Optional[float] = None  # start time (seconds since midnight) of the event
    mAvgPathWetness: Optional[float] = None  # average wetness on the main path

    mExpansion: Optional[List[int]] = None  # for future use
    pointer2: Optional[List[int]] = None

class rF2VehicleScoring(BaseModel):
    mID: Optional[int] = None  # slot ID
    mDriverName: Optional[bytes] = None  # driver name
    mVehicleName: Optional[bytes] = None  # vehicle name
    mTotalLaps: Optional[int] = None  # laps completed
    mSector: Optional[int] = None  # sector
    mFinishStatus: Optional[int] = None  # finish status
    mLapDist: Optional[float] = None  # current distance around the track
    mPathLateral: Optional[float] = None  # lateral position with respect to the "center" path
    mTrackEdge: Optional[float] = None  # track edge w.r.t. "center" path on the same side of the track as the vehicle

    mBestSector1: Optional[float] = None  # best sector 1
    mBestSector2: Optional[float] = None  # best sector 2 (plus sector 1)
    mBestLapTime: Optional[float] = None  # best lap time
    mLastSector1: Optional[float] = None  # last sector 1
    mLastSector2: Optional[float] = None  # last sector 2 (plus sector 1)
    mLastLapTime: Optional[float] = None  # last lap time
    mCurSector1: Optional[float] = None  # current sector 1 if valid
    mCurSector2: Optional[float] = None  # current sector 2 (plus sector 1) if valid

    mNumPitstops: Optional[int] = None  # number of pitstops made
    mNumPenalties: Optional[int] = None  # number of outstanding penalties
    mIsPlayer: Optional[bool] = None  # is this the player's vehicle

    mControl: Optional[int] = None  # who's in control
    mInPits: Optional[bool] = None  # between pit entrance and pit exit
    mPlace: Optional[int] = None  # 1-based position
    mVehicleClass: Optional[bytes] = None  # vehicle class

    # Dash Indicators
    mTimeBehindNext: Optional[float] = None  # time behind the vehicle in the next higher place
    mLapsBehindNext: Optional[int] = None  # laps behind the vehicle in the next higher place
    mTimeBehindLeader: Optional[float] = None  # time behind the leader
    mLapsBehindLeader: Optional[int] = None  # laps behind the leader
    mLapStartET: Optional[float] = None  # time this lap was started

    # Position and derivatives
    mPos: Optional[rF2Vec3] = None  # world position in meters
    mLocalVel: Optional[rF2Vec3] = None  # velocity in local vehicle coordinates
    mLocalAccel: Optional[rF2Vec3] = None  # acceleration in local vehicle coordinates

    # Orientation and derivatives
    mOri: Optional[List[rF2Vec3]] = None  # rows of the orientation matrix
    mLocalRot: Optional[rF2Vec3] = None  # rotation in local vehicle coordinates
    mLocalRotAccel: Optional[rF2Vec3] = None  # rotational acceleration in local vehicle coordinates

    mHeadlights: Optional[int] = None  # status of headlights
    mPitState: Optional[int] = None  # pit state
    mServerScored: Optional[int] = None  # whether this vehicle is being scored by the server
    mIndividualPhase: Optional[int] = None  # game phases

    mQualification: Optional[int] = None  # 1-based qualification
    mTimeIntoLap: Optional[float] = None  # estimated time into the lap
    mEstimatedLapTime: Optional[float] = None  # estimated laptime

    mPitGroup: Optional[bytes] = None  # pit group
    mFlag: Optional[int] = None  # primary flag being shown to the vehicle
    mUnderYellow: Optional[bool] = None  # whether this car has taken a full-course caution flag
    mCountLapFlag: Optional[int] = None  # count lap and time flag
    mInGarageStall: Optional[bool] = None  # within the correct garage stall

    mUpgradePack: Optional[List[int]] = None  # coded upgrades

    mPitLapDist: Optional[float] = None  # location of the pit in terms of lap distance
    mBestLapSector1: Optional[float] = None  # sector 1 time from the best lap
    mBestLapSector2: Optional[float] = None  # sector 2 time from the best lap

    mExpansion: Optional[List[int]] = None  # for future use

class rF2Scoring(BaseModel):
    mVersionUpdateBegin: int # Incremented right before the buffer is written to
    mVersionUpdateEnd: int # Incremented after the buffer write is done
    mBytesUpdatedHint: int # How many bytes of the structure were written during the last update
    mScoringInfo: Optional[rF2ScoringInfo] = None
    mVehicles: Optional[List[rF2VehicleScoring]] = None

    @classmethod
    def build(cls, a: Any):
        return rF2Scoring.model_validate_json(json.dumps(a, cls=CDataJSONEncoder), strict=True)

class rF2Telemetry(BaseModel):
    mVersionUpdateBegin: int # Incremented right before the buffer is written to
    mVersionUpdateEnd: int # Incremented after the buffer write is done
    mBytesUpdatedHint: int # How many bytes of the structure were written during the last update
    mNumVehicles: int # current number of vehicles
    mVehicles: Optional[List[rF2VehicleTelemetry]] = None

    @classmethod
    def build(cls, a: Any):
        return rF2Telemetry.model_validate_json(json.dumps(a, cls=CDataJSONEncoder), strict=True)
