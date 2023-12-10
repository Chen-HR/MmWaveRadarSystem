import time
import datetime
import dataclasses

from Ti_MmWave_Demo_Driver import Ti_MmWave as mmWave

if __name__ == '__main__':
  import matplotlib.pyplot
  import matplotlib.collections
  import matplotlib.animation

class Timer:
  """Simple timer class to measure elapsed time."""
  def __init__(self):
    self.starttime = 0.0
  def start(self):
    """Start the timer."""
    self.starttime = time.time()
  def now(self):
    """Get the elapsed time since starting the timer."""
    return time.time() - self.starttime

@dataclasses.dataclass
class Range:
  min: int | float = 0
  max: int | float = 1

@dataclasses.dataclass
class AreaLimit_3d:
  x: Range = dataclasses.field(default_factory=Range)
  y: Range = dataclasses.field(default_factory=Range)
  z: Range = dataclasses.field(default_factory=Range)

class MmWaveRadarSystem:
  def __init__(self, mmWaveDevice_platform: str, mmWaveDevice_Ctrl_port_name: str, mmWaveDevice_Data_port_name: str, mmWaveDevice_profile: str, mmWaveDevice_Ctrl_port_baudrate: int = 115200, mmWaveDevice_Data_port_baudrate: int = 921600, mmWaveDevice_Send_timeInterval: int | float = 0.025, mmWaveDevice_Buffering_timeInterval: int | float = 0.1, mmWaveDevice_Parse_timeInterval: int | float = 0.5, threshold_dB: int | float = 14, removeStaticClutter: bool = True, framePeriodicity_ms: int = 1000, log_enable: bool = False):
    self.log_enable = log_enable
    if self.log_enable: 
      timer = Timer()
      timer.start()
    self.mmWaveDevice = mmWave(mmWaveDevice_platform, mmWaveDevice_Ctrl_port_name, mmWaveDevice_Data_port_name, mmWaveDevice_Ctrl_port_baudrate, mmWaveDevice_Data_port_baudrate, mmWaveDevice_Send_timeInterval, mmWaveDevice_Buffering_timeInterval, mmWaveDevice_Parse_timeInterval, log_enable=log_enable)
    if self.log_enable: print(f"[{datetime.datetime.now()}] Millimeter wave device connection completed, using a total of {timer.now()} second")
    self.profile = mmWaveDevice_profile
    self.threshold_dB = threshold_dB
    self.removeStaticClutter = removeStaticClutter
    self.framePeriodicity_ms = framePeriodicity_ms
    self.send_timeInterval = mmWaveDevice_Send_timeInterval
    self.buffering_timeInterval = mmWaveDevice_Buffering_timeInterval
    self.parse_timeInterval = mmWaveDevice_Parse_timeInterval
    self.mmWaveDevice.sensorStop()
    self.mmWaveDevice.Ctrl_Load_file(mmWaveDevice_profile)
    self.mmWaveDevice.set_cfarRangeThreshold_dB(threshold_dB)
    self.mmWaveDevice.set_removeStaticClutter(removeStaticClutter)
    self.mmWaveDevice.set_framePeriodicity(framePeriodicity_ms)
    self.mmWaveDevice.Ctrl_Send()
    if self.log_enable: print(f"[{datetime.datetime.now()}] Millimeter wave device configuration completed, used for a total of {timer.now()} second")
  def start(self):
    if self.mmWaveDevice.State != "Sensor_Start": 
      if self.log_enable: print(f"[{datetime.datetime.now()}] Start millimeter wave device")
      self.mmWaveDevice.sensorStart()
  def stop(self):
    if self.mmWaveDevice.State != "Sensor_Stop": 
      if self.log_enable: print(f"[{datetime.datetime.now()}] Turn off millimeter wave devices")
      self.mmWaveDevice.sensorStop()
  def __del__(self):
    self.stop()
    if self.log_enable: print(f"[{datetime.datetime.now()}] Release millimeter wave devices")
    del self.mmWaveDevice

  def detectedPoints(self, wait_new: bool = True) -> list[tuple]:
    return self.mmWaveDevice.get_detectedPoints(wait_new)

if __name__ == "__main__":
  detectionLimit = AreaLimit_3d(Range(-5, 5), Range(0, 5), Range(-5, 5))

  mmWaveRadarSystem = MmWaveRadarSystem("xWR14xx", "COM3", "COM4", "Ti_MmWave_Demo_Driver\Profile\Profile-4.cfg", log_enable=True)

  mmWaveRadarSystem.start()

  def plot_3d(detectionLimit: AreaLimit_3d, mmWaveRadarSystem: MmWaveRadarSystem):
    figure: matplotlib.pyplot.Figure = matplotlib.pyplot.figure()
    figure.set_label("mmWave Radar detection chart")
    axes: matplotlib.pyplot.Axes = figure.add_subplot(111, projection="3d")
    axes.set_title("Detection distribution map")
    axes.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel="X (Unit: Meter)")
    axes.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel="Y (Unit: Meter)")
    axes.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel="Z (Unit: Meter)")
    def update(frame, scatter: matplotlib.collections.PathCollection, device: mmWaveRadarSystem):
      detectedPoints = mmWaveRadarSystem.detectedPoints()
      scatter._offsets3d = tuple(zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
    animation = matplotlib.animation.FuncAnimation(figure, update, fargs=(axes.scatter([], [], [], label='Detection Object'), mmWaveRadarSystem), interval=mmWaveRadarSystem.framePeriodicity_ms*mmWaveRadarSystem.parse_timeInterval, cache_frame_data=False)
    axes.legend()
    matplotlib.pyplot.show()

  def plot_2d(detectionLimit: AreaLimit_3d, mmWaveRadarSystem: MmWaveRadarSystem):
    figure: matplotlib.pyplot.Figure = matplotlib.pyplot.figure()
    figure.set_label("mmWave Radar detection chart")
    axes: matplotlib.pyplot.Axes = figure.add_subplot(111)
    def update(frame, axes: matplotlib.pyplot.Axes, device: mmWaveRadarSystem):
      detectedPoints = mmWaveRadarSystem.detectedPoints()
      detectedPoints_ = tuple(zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
      axes.clear()
      axes.set_title("Detection distribution map")
      axes.set_xlabel("X (Unit: Meter)")
      axes.set_ylabel("Y (Unit: Meter)")
      axes.set_xlim(detectionLimit.x.min, detectionLimit.x.max)
      axes.set_ylim(detectionLimit.y.min, detectionLimit.y.max)
      axes.scatter(detectedPoints_[0], detectedPoints_[1], label="Detection Object")
      axes.legend()
    animation = matplotlib.animation.FuncAnimation(figure, update, fargs=(axes, mmWaveRadarSystem), interval=mmWaveRadarSystem.framePeriodicity_ms*mmWaveRadarSystem.parse_timeInterval, cache_frame_data=False)
    matplotlib.pyplot.show()

  plot_3d(detectionLimit, mmWaveRadarSystem)
  plot_2d(detectionLimit, mmWaveRadarSystem)

  mmWaveRadarSystem.stop()

  del mmWaveRadarSystem
