# 🛏️ Occupancy Helper for Home Assistant

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=adromir&repository=ha-occupancy-helper&category=integration)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/default)
[![GitHub Release](https://img.shields.io/github/v/release/adromir/ha-occupancy-helper?style=for-the-badge&color=blue)](https://github.com/adromir/ha-occupancy-helper/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/adromir/ha-occupancy-helper)

A powerful, native **Home Assistant Helper Integration** that consolidates multiple motion detectors, mmWave presence sensors, door/window contacts, or boolean entities into an intelligent, consolidated room occupancy entity with configurable evaluation logic, auto-clearing hold time (`delay_off`), and dynamic state icons.

Eliminates repetitive, complex YAML Jinja2 template sensors and manual timers for room occupancy!

---

## 🎯 Why You Need This

Accurate room presence in smart homes almost always requires **combining multiple sensors**:
- An mmWave radar sensor for micro-movements
- A PIR sensor for rapid entrance detection
- A bed pressure mat or chair sensor
- A door contact to prevent turning off lights while the door is closed

Until now, achieving this in Home Assistant required tedious YAML template sensors with hardcoded logic and templates:

```yaml
# ❌ Tedious, static YAML template sensor:
template:
  - binary_sensor:
      - name: "Belegung Schlafzimmer"
        unique_id: "presence_bedroom_occupancy_logic"
        device_class: occupancy
        delay_off: "00:05:00"
        state: >
          {{ is_state('binary_sensor.schlafzimmer_presence', 'on') 
              or is_state('binary_sensor.bewegungsmelder_schlafzimmer_motion', 'on') }}
        icon: >
          {{ 'mdi:bed' if is_state('binary_sensor.schlafzimmer_presence', 'on') else 'mdi:bed-empty' }}
```

With the **Occupancy Helper**, you create and configure this entire logic in seconds right inside the Home Assistant UI without touching YAML files or restarting Home Assistant!

---

## ✨ Key Features & Advantages

- 🎛️ **Native Helper Integration (`integration_type: helper`)**: Appears natively in Home Assistant under **Settings > Devices & Services > Helpers > Create Helper > Occupancy Helper**.
- 🔀 **Configurable Logic**:
  - **`OR` (Default)**: Room is marked occupied if **any** sensor detects motion or presence.
  - **`AND`**: Room is marked occupied only when **all** selected conditions are active.
- ⏱️ **Integrated Hold Time (`delay_off`)**: Native duration countdown that keeps the room occupied after sensors go idle (e.g. 5 minutes). Automatically cancels and resets if any movement is detected during the countdown.
- 🎨 **Dynamic Contextual Icons**: Choose custom icons for both active and clear states (e.g. `mdi:bed` when occupied, `mdi:bed-empty` when clear; or `mdi:sofa` / `mdi:sofa-outline`).
- 🏷️ **Rich State Attributes**: Exposes `sensors`, `active_sensors`, `logic`, `delay_off`, `delay_off_active`, and `last_trigger_sensor`.
- ⚙️ **Full Reconfiguration**: Modify sensors, duration, or logic at any time via the UI Options Flow without reloading Home Assistant.
- 🌐 **Bilingual Support**: Fully localized in English and German.

---

## 📦 Installation

### Method 1: HACS (Recommended)

1. Click the button below to add this repository directly to HACS:

   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=adromir&repository=ha-occupancy-helper&category=integration)

2. Or manually in HACS:
   - Go to **HACS** > **Integrations** > **Three dots menu (top right)** > **Custom repositories**.
   - URL: `https://github.com/adromir/ha-occupancy-helper`
   - Type: `Integration`
   - Click **Add**, then find **Occupancy Helper** and click **Download**.
3. **Restart Home Assistant**.

### Method 2: Manual Installation
1. Copy the `custom_components/occupancy_helper` directory into your Home Assistant `<config>/custom_components/` folder.
2. Restart Home Assistant.

---

## 🚀 How to Use

1. In Home Assistant, navigate to **Settings** > **Devices & Services** > **Helpers**.
2. Click **Create Helper** (bottom right) and select **Occupancy Helper**.
3. Configure your room:
   - **Name**: e.g. `Belegung Schlafzimmer`
   - **Monitored Sensors**: Pick all relevant presence, motion, or door sensors (e.g. `binary_sensor.schlafzimmer_presence`, `binary_sensor.schlafzimmer_motion`).
   - **Evaluation Logic**: Choose `OR` or `AND`.
   - **Delay Off Duration**: Set desired hold time (e.g., `00:05:00`).
   - **Occupied Icon**: e.g., `mdi:bed`
   - **Clear / Idle Icon**: e.g., `mdi:bed-empty`
4. Click **Submit**. Your new occupancy entity (`binary_sensor.belegung_schlafzimmer`) is ready for all your heating, lighting, and security automations!

---

## 📄 Disclaimer

This is a custom community integration and is not officially affiliated with or endorsed by Nabu Casa or Home Assistant.

---

## 📜 License

This project is open-source under the [MIT License](LICENSE).

**Author**: [Adromir](https://github.com/adromir)  
Website: [https://github.com/adromir](https://github.com/adromir)
