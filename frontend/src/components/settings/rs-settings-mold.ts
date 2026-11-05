/**
 * rs-settings-mold – Mold risk detection & prevention settings.
 */
import { html, nothing } from "lit";
import { customElement, property } from "lit/decorators.js";
import { RsSettingsBase } from "./rs-settings-base";
import type { HomeAssistant } from "../../types";
import { localize, type TranslationKey } from "../../utils/localize";
import { getSelectValue } from "../../utils/events";
import { tempUnit, toDisplayDelta } from "../../utils/temperature";

// DIN 4108-2 temperature factor f_Rsi of the coldest spot (corner, window reveal) per insulation level.
const INSULATION_LEVELS = [
  { f_rsi: 0.65, key: "mold.insulation_poor" },
  { f_rsi: 0.8, key: "mold.insulation_standard" },
  { f_rsi: 0.9, key: "mold.insulation_good" },
] as const;

@customElement("rs-settings-mold")
export class RsSettingsMold extends RsSettingsBase {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ type: Boolean }) public moldDetectionEnabled = false;
  @property({ type: Number }) public moldHumidityThreshold = 70;
  @property({ type: Number }) public moldFRsi = 0.8;
  @property({ type: Number }) public moldSustainedMinutes = 30;
  @property({ type: Number }) public dehumidifierDelayMinutes = 10;
  @property({ type: Number }) public dehumidifierMinOnMinutes = 10;
  @property({ type: Number }) public dehumidifierMinOffMinutes = 5;
  @property({ type: Boolean }) public dehumidifierQuietEnabled = false;
  @property({ type: String }) public dehumidifierQuietStart = "22:00";
  @property({ type: String }) public dehumidifierQuietEnd = "07:00";
  @property({ type: Boolean }) public dehumidifierVentilationNotify = true;
  @property({ type: Boolean }) public dehumidifierPreferVentilation = false;
  @property({ type: Boolean }) public moldPreventionEnabled = false;
  @property({ type: String }) public moldPreventionIntensity: "light" | "medium" | "strong" =
    "medium";

  render() {
    const l = this.hass.language;

    return html`
      <!-- Detection section -->
      <div class="settings-section first">
        <div class="toggle-row">
          <div class="toggle-text">
            <span class="toggle-label">
              <ha-icon
                icon="mdi:bell-alert"
                style="--mdc-icon-size: 18px; vertical-align: middle; margin-right: 4px"
              ></ha-icon>
              ${localize("mold.detection", l)}
            </span>
            <span class="toggle-hint">${localize("mold.detection_desc", l)}</span>
          </div>
          <ha-switch
            .checked=${this.moldDetectionEnabled}
            @change=${(e: Event) =>
              this._fire("moldDetectionEnabled", (e.target as HTMLInputElement).checked)}
          ></ha-switch>
        </div>
        ${
          this.moldDetectionEnabled
            ? html`
                <div class="threshold-grid" style="margin-top: 12px">
                  <div class="threshold-field">
                    <ha-textfield
                      .value=${String(this.moldHumidityThreshold)}
                      .label=${localize("mold.threshold", l)}
                      .suffix=${"%"}
                      type="number"
                      step="1"
                      min="50"
                      max="90"
                      @change=${(e: Event) => {
                        const v = parseFloat((e.target as HTMLInputElement).value);
                        if (!isNaN(v) && v >= 50 && v <= 90) this._fire("moldHumidityThreshold", v);
                      }}
                    ></ha-textfield>
                    <span class="field-hint">${localize("mold.threshold_hint", l)}</span>
                  </div>
                  <div class="threshold-field">
                    <ha-textfield
                      .value=${String(this.moldSustainedMinutes)}
                      .label=${localize("mold.sustained", l)}
                      .suffix=${"min"}
                      type="number"
                      step="5"
                      min="5"
                      max="120"
                      @change=${(e: Event) => {
                        const v = parseInt((e.target as HTMLInputElement).value, 10);
                        if (!isNaN(v) && v >= 5 && v <= 120) this._fire("moldSustainedMinutes", v);
                      }}
                    ></ha-textfield>
                    <span class="field-hint">${localize("mold.sustained_hint", l)}</span>
                  </div>
                </div>
              `
            : nothing
        }
      </div>

      <!-- Prevention section -->
      <div class="settings-section">
        <div class="toggle-row">
          <div class="toggle-text">
            <span class="toggle-label">
              <ha-icon
                icon="mdi:shield-check"
                style="--mdc-icon-size: 18px; vertical-align: middle; margin-right: 4px"
              ></ha-icon>
              ${localize("mold.prevention", l)}
            </span>
            <span class="toggle-hint">${localize("mold.prevention_desc", l)}</span>
          </div>
          <ha-switch
            .checked=${this.moldPreventionEnabled}
            @change=${(e: Event) =>
              this._fire("moldPreventionEnabled", (e.target as HTMLInputElement).checked)}
          ></ha-switch>
        </div>
        ${
          this.moldPreventionEnabled
            ? html`
                <div style="margin-top: 12px; display: flex; flex-direction: column; gap: 4px;">
                  <ha-select
                    style="width: 100%;"
                    .value=${this.moldPreventionIntensity}
                    .label=${localize("mold.intensity", l)}
                    .options=${[
                      {
                        value: "light",
                        label: localize("mold.intensity_light", l, {
                          delta: String(toDisplayDelta(1, this.hass)),
                          unit: tempUnit(this.hass),
                        }),
                      },
                      {
                        value: "medium",
                        label: localize("mold.intensity_medium", l, {
                          delta: String(toDisplayDelta(2, this.hass)),
                          unit: tempUnit(this.hass),
                        }),
                      },
                      {
                        value: "strong",
                        label: localize("mold.intensity_strong", l, {
                          delta: String(toDisplayDelta(3, this.hass)),
                          unit: tempUnit(this.hass),
                        }),
                      },
                    ]}
                    fixedMenuPosition
                    @selected=${(e: Event) => {
                      const v = getSelectValue(e) as "light" | "medium" | "strong";
                      if (v && v !== this.moldPreventionIntensity)
                        this._fire("moldPreventionIntensity", v);
                    }}
                    @closed=${(e: Event) => e.stopPropagation()}
                  >
                    <ha-list-item value="light"
                      >${localize("mold.intensity_light", l, {
                        delta: String(toDisplayDelta(1, this.hass)),
                        unit: tempUnit(this.hass),
                      })}</ha-list-item
                    >
                    <ha-list-item value="medium"
                      >${localize("mold.intensity_medium", l, {
                        delta: String(toDisplayDelta(2, this.hass)),
                        unit: tempUnit(this.hass),
                      })}</ha-list-item
                    >
                    <ha-list-item value="strong"
                      >${localize("mold.intensity_strong", l, {
                        delta: String(toDisplayDelta(3, this.hass)),
                        unit: tempUnit(this.hass),
                      })}</ha-list-item
                    >
                  </ha-select>
                  <span class="field-hint">${localize("mold.intensity_hint", l)}</span>
                </div>
              `
            : nothing
        }
      </div>

      <!-- Dehumidifier section (rooms enable their dehumidifier in the room settings) -->
      <div class="settings-section">
        <div class="toggle-text">
          <span class="toggle-label">
            <ha-icon icon="mdi:air-humidifier"></ha-icon>
            ${localize("mold.dehumidifier", l)}
          </span>
          <span class="toggle-hint">${localize("mold.dehumidifier_desc", l)}</span>
        </div>
        <div class="threshold-grid three" style="margin-top: 12px">
          ${this._minutesField("dehumidifierDelayMinutes", this.dehumidifierDelayMinutes, "mold.dehumidifier_delay", 120)}
          ${this._minutesField("dehumidifierMinOnMinutes", this.dehumidifierMinOnMinutes, "mold.dehumidifier_min_on", 60)}
          ${this._minutesField("dehumidifierMinOffMinutes", this.dehumidifierMinOffMinutes, "mold.dehumidifier_min_off", 60)}
        </div>
        <div class="toggle-row" style="margin-top: 16px">
          <div class="toggle-text">
            <span class="toggle-label">
              <ha-icon icon="mdi:sleep"></ha-icon>
              ${localize("mold.dehumidifier_quiet", l)}
            </span>
            <span class="toggle-hint">${localize("mold.dehumidifier_quiet_desc", l)}</span>
          </div>
          <ha-switch
            .checked=${this.dehumidifierQuietEnabled}
            @change=${(e: Event) =>
              this._fire("dehumidifierQuietEnabled", (e.target as HTMLInputElement).checked)}
          ></ha-switch>
        </div>
        ${
          this.dehumidifierQuietEnabled
            ? html`
                <div class="threshold-grid" style="margin-top: 12px">
                  ${this._timeField("dehumidifierQuietStart", this.dehumidifierQuietStart, "mold.dehumidifier_quiet_start")}
                  ${this._timeField("dehumidifierQuietEnd", this.dehumidifierQuietEnd, "mold.dehumidifier_quiet_end")}
                </div>
              `
            : nothing
        }
        <div class="toggle-row" style="margin-top: 16px">
          <div class="toggle-text">
            <span class="toggle-label">
              <ha-icon icon="mdi:window-open-variant"></ha-icon>
              ${localize("mold.ventilation_notify", l)}
            </span>
            <span class="toggle-hint">${localize("mold.ventilation_notify_desc", l)}</span>
          </div>
          <ha-switch
            .checked=${this.dehumidifierVentilationNotify}
            @change=${(e: Event) =>
              this._fire("dehumidifierVentilationNotify", (e.target as HTMLInputElement).checked)}
          ></ha-switch>
        </div>
        <div class="toggle-row" style="margin-top: 16px">
          <div class="toggle-text">
            <span class="toggle-label">
              <ha-icon icon="mdi:weather-windy"></ha-icon>
              ${localize("mold.prefer_ventilation", l)}
            </span>
            <span class="toggle-hint">${localize("mold.prefer_ventilation_desc", l)}</span>
          </div>
          <ha-switch
            .checked=${this.dehumidifierPreferVentilation}
            @change=${(e: Event) =>
              this._fire("dehumidifierPreferVentilation", (e.target as HTMLInputElement).checked)}
          ></ha-switch>
        </div>
      </div>

      ${
        this.moldDetectionEnabled || this.moldPreventionEnabled
          ? html`
              <div class="settings-section">
                <div style="display: flex; flex-direction: column; gap: 4px;">
                  <ha-select
                    style="width: 100%;"
                    .value=${this._insulationValue()}
                    .label=${localize("mold.insulation", l)}
                    .options=${INSULATION_LEVELS.map((lvl) => ({
                      value: String(lvl.f_rsi),
                      label: localize(lvl.key, l),
                    }))}
                    fixedMenuPosition
                    @selected=${(e: Event) => {
                      const v = parseFloat(getSelectValue(e));
                      if (!isNaN(v) && v !== this.moldFRsi) this._fire("moldFRsi", v);
                    }}
                    @closed=${(e: Event) => e.stopPropagation()}
                  >
                    ${INSULATION_LEVELS.map(
                      (lvl) =>
                        html`<ha-list-item value=${String(lvl.f_rsi)}
                          >${localize(lvl.key, l)}</ha-list-item
                        >`,
                    )}
                  </ha-select>
                  <span class="field-hint">${localize("mold.insulation_hint", l)}</span>
                </div>
              </div>
            `
          : nothing
      }
    `;
  }

  private _minutesField(key: string, value: number, label: TranslationKey, max: number) {
    const l = this.hass.language;
    return html`
      <div class="threshold-field">
        <ha-textfield
          .value=${String(value)}
          .label=${localize(label, l)}
          .suffix=${"min"}
          type="number"
          step="1"
          min="0"
          max=${max}
          @change=${(e: Event) => {
            const v = parseInt((e.target as HTMLInputElement).value, 10);
            if (!isNaN(v) && v >= 0 && v <= max) this._fire(key, v);
          }}
        ></ha-textfield>
        <span class="field-hint">${localize(`${label}_hint` as TranslationKey, l)}</span>
      </div>
    `;
  }

  private _timeField(key: string, value: string, label: TranslationKey) {
    return html`
      <div class="threshold-field">
        <ha-textfield
          .value=${value}
          .label=${localize(label, this.hass.language)}
          type="time"
          @change=${(e: Event) => {
            const v = (e.target as HTMLInputElement).value;
            if (/^([01]\d|2[0-3]):[0-5]\d$/.test(v)) this._fire(key, v);
          }}
        ></ha-textfield>
      </div>
    `;
  }

  private _insulationValue(): string {
    const nearest = INSULATION_LEVELS.reduce((best, lvl) =>
      Math.abs(lvl.f_rsi - this.moldFRsi) < Math.abs(best.f_rsi - this.moldFRsi) ? lvl : best,
    );
    return String(nearest.f_rsi);
  }

  static styles = [RsSettingsBase.settingsBaseStyles];
}

declare global {
  interface HTMLElementTagNameMap {
    "rs-settings-mold": RsSettingsMold;
  }
}
