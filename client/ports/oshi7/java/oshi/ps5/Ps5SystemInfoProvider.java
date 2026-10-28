/* SPDX-License-Identifier: GPL-3.0-or-later */
package oshi.ps5;
import oshi.hardware.HardwareAbstractionLayer;
import oshi.software.os.OperatingSystem;
import oshi.spi.SystemInfoProvider;
/** OSHI 7's supported SPI, enabled only after native PS5 CPU identity handoff. */
public final class Ps5SystemInfoProvider implements SystemInfoProvider {
 public boolean isAvailable(){return Boolean.getBoolean("oshi.ps5");}
 public int getPriority(){return 100;}
 public HardwareAbstractionLayer getHardware(){if(!isAvailable())throw new UnsupportedOperationException("PS5 CPU identity unavailable");return Ps5Hardware.create();}
 public OperatingSystem getOperatingSystem(){throw new UnsupportedOperationException("PS5 operating-system metrics are not ported");}
}
