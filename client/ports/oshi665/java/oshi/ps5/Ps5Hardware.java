/* SPDX-License-Identifier: GPL-3.0-or-later */
package oshi.ps5;
import java.util.List;
import oshi.hardware.*;

/** Narrow dependency platform provider. Unsupported telemetry never becomes invented measurements. */
public final class Ps5Hardware implements HardwareAbstractionLayer {
 private final CentralProcessor cpu;
 private Ps5Hardware(CentralProcessor cpu){this.cpu=cpu;}
 private static UnsupportedOperationException unsupported(){return new UnsupportedOperationException("PS5 OSHI supports CPU identity and OS-visible logical count only");}
 public static HardwareAbstractionLayer create(){
  String brand=System.getProperty("ps5.cpu.brand",""),vendor=System.getProperty("ps5.cpu.vendor",""),signature=System.getProperty("ps5.cpu.signature","");
  int count=Integer.parseInt(System.getProperty("ps5.cpu.logical","0"));
  if(brand.isBlank()||brand.length()>95||!brand.chars().allMatch(c->c>=32&&c<=126)||count<1||count>4096||!signature.matches("[A-Fa-f0-9]{8}"))throw unsupported();
  var id=new CentralProcessor.ProcessorIdentifier(vendor,brand,System.getProperty("ps5.cpu.family",""),System.getProperty("ps5.cpu.model",""),System.getProperty("ps5.cpu.stepping",""),signature,true,-1);
  return new Ps5Hardware(new Cpu(id,count));
 }
 public CentralProcessor getProcessor(){return cpu;}
 public ComputerSystem getComputerSystem(){throw unsupported();}
 public GlobalMemory getMemory(){throw unsupported();}
 public List<PowerSource> getPowerSources(){throw unsupported();}
 public List<HWDiskStore> getDiskStores(){throw unsupported();}
 public List<LogicalVolumeGroup> getLogicalVolumeGroups(){throw unsupported();}
 public List<NetworkIF> getNetworkIFs(){throw unsupported();}
 public List<NetworkIF> getNetworkIFs(boolean all){throw unsupported();}
 public List<Display> getDisplays(){throw unsupported();}
 public Sensors getSensors(){throw unsupported();}
 public List<UsbDevice> getUsbDevices(boolean tree){throw unsupported();}
 public List<SoundCard> getSoundCards(){throw unsupported();}
 public List<GraphicsCard> getGraphicsCards(){throw unsupported();}
 private static final class Cpu implements CentralProcessor {
  private final ProcessorIdentifier id;private final int count;
  Cpu(ProcessorIdentifier id,int count){this.id=id;this.count=count;}
  public ProcessorIdentifier getProcessorIdentifier(){return id;}
  public int getLogicalProcessorCount(){return count;}
  public long getMaxFreq(){throw unsupported();}
  public long[] getCurrentFreq(){throw unsupported();}
  public List<LogicalProcessor> getLogicalProcessors(){throw unsupported();}
  public List<PhysicalProcessor> getPhysicalProcessors(){throw unsupported();}
  public List<ProcessorCache> getProcessorCaches(){throw unsupported();}
  public List<String> getFeatureFlags(){throw unsupported();}
  public double getSystemCpuLoadBetweenTicks(long[] old){throw unsupported();}
  public long[] getSystemCpuLoadTicks(){throw unsupported();}
  public double[] getSystemLoadAverage(int n){throw unsupported();}
  public double[] getProcessorCpuLoadBetweenTicks(long[][] old){throw unsupported();}
  public long[][] getProcessorCpuLoadTicks(){throw unsupported();}
  public int getPhysicalProcessorCount(){throw unsupported();}
  public int getPhysicalPackageCount(){throw unsupported();}
  public long getContextSwitches(){throw unsupported();}
  public long getInterrupts(){throw unsupported();}
 }
}
