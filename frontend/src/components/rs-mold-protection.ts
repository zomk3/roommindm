/**
 * rs-mold-protection – a room's mold protection: prevention heating and the dehumidifier.
 *
 * Lives in the room's "Schedule & temperatures" section. The dehumidifier device and its
 * tank sensor are chosen under Devices, the humidity sensor under Sensors.
 */
import { LitElement, html, css, nothing } from "lit";
import { customElement, property } from "lit/decorators.js";
import type { HomeAssistant } from "../types";
import { localize } from "../utils/localize";
import { toggleFieldStyles } from "../styles/toggle-field-styles";
import "./shared/rs-toggle-row";

@customElement("rs-mold-protection")
export class RsMoldProtection extends LitElement {
  @property({ attribute: false }) public hass!: HomeAssistant;
  @property({ type: Boolean }) public editing = false;
  @property({ type: String }) public humiditySensor = "";
  @property({ type: String }) public dehumidifierEntity = "";
  @property({ type: Boolean }) public dehumidifierEnabled = false;
  @property({ type: Number }) public dehumidifierLower = 50;
  @property({ type: Number }) public dehumidifierUpper = 60;
  @property({ type: Boolean }) public moldPreventionHeating = true;

  static styles = [
    toggleFieldStyles,
    css`
      :host {
        display: block;
      }
      .section-subtitle {
        font-size: 12px;
        font-weight: 500;
        color: var(--secondary-text-color);
        margin: 16px 0 8px 0;
        text-transform: uppercase;
        letter-spacing: 0.4px;
      }
      .edit-body {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }
      .view-row {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;
        padding: 2px 0;
      }
      .view-row ha-icon {
        --mdc-icon-size: 18px;
        color: var(--secondary-text-color);
      }
      .view-row.off {
        color: var(--secondary-text-color);
      }
    `,
  ];

  render() {
    const l = this.hass.language;
    return html`
      <div class="section-subtitle">${localize("mold.title", l)}</div>
      ${this.editing ? this._renderEdit(l) : this._renderView(l)}
    `;
  }

  private _renderView(l: string) {
    const name =
      (this.hass.states[this.dehumidifierEntity]?.attributes?.friendly_name as string) ||
      this.dehumidifierEntity;
    return html`
      <div class="view-row ${this.moldPreventionHeating ? "" : "off"}">
        <ha-icon icon="mdi:shield-check"></ha-icon>
        ${localize("mold.room_heating_title", l)}:
        ${localize(this.moldPreventionHeating ? "common.on" : "common.off", l)}
      </div>
      ${
        this.dehumidifierEntity
          ? html`<div class="view-row ${this.dehumidifierEnabled ? "" : "off"}">
              <ha-icon icon="mdi:air-humidifier"></ha-icon>
              ${localize("dehumidifier.enabled", l)}:
              ${
                this.dehumidifierEnabled
                  ? html`${name} · ${this.dehumidifierLower}–${this.dehumidifierUpper}%`
                  : localize("common.off", l)
              }
            </div>`
          : nothing
      }
    `;
  }

  private _renderEdit(l: string) {
    const dehumidifierReady = !!this.dehumidifierEntity && !!this.humiditySensor;
    return html`
      <div class="edit-body">
        <rs-toggle-row
          .label=${localize("mold.room_heating_title", l)}
          .hint=${localize("mold.room_heating_hint", l)}
          .checked=${this.moldPreventionHeating}
          @toggle-changed=${(e: CustomEvent<boolean>) => {
            e.stopPropagation();
            this._fire("mold_prevention_heating", e.detail);
          }}
        ></rs-toggle-row>
        <rs-toggle-row
          .label=${localize("dehumidifier.enabled", l)}
          .hint=${localize(dehumidifierReady ? "dehumidifier.hint" : "dehumidifier.requires", l)}
          .checked=${this.dehumidifierEnabled}
          .disabled=${!dehumidifierReady}
          @toggle-changed=${(e: CustomEvent<boolean>) => {
            e.stopPropagation();
            this._fire("dehumidifier_enabled", e.detail);
          }}
        ></rs-toggle-row>
        ${
          this.dehumidifierEnabled
            ? html`
                <div class="threshold-grid">
                  <div class="threshold-field">
                    <ha-textfield
                      type="number"
                      step="1"
                      min="1"
                      max=${this.dehumidifierUpper - 1}
                      suffix="%"
                      .label=${localize("dehumidifier.lower", l)}
                      .value=${String(this.dehumidifierLower)}
                      @change=${(e: Event) => this._onBoundChange(e, true)}
                    ></ha-textfield>
                  </div>
                  <div class="threshold-field">
                    <ha-textfield
                      type="number"
                      step="1"
                      min=${this.dehumidifierLower + 1}
                      max="100"
                      suffix="%"
                      .label=${localize("dehumidifier.upper", l)}
                      .value=${String(this.dehumidifierUpper)}
                      @change=${(e: Event) => this._onBoundChange(e, false)}
                    ></ha-textfield>
                  </div>
                </div>
              `
            : nothing
        }
      </div>
    `;
  }

  private _onBoundChange(e: Event, lower: boolean) {
    const v = parseInt((e.target as HTMLInputElement).value, 10);
    const ok = lower
      ? v >= 1 && v < this.dehumidifierUpper
      : v > this.dehumidifierLower && v <= 100;
    if (!isNaN(v) && ok) {
      this._fire(lower ? "dehumidifier_lower_bound" : "dehumidifier_upper_bound", v);
    }
  }

  private _fire(key: string, value: boolean | number) {
    this.dispatchEvent(
      new CustomEvent("sensor-changed", {
        detail: { key, value },
        bubbles: true,
        composed: true,
      }),
    );
  }
}

declare global {
  interface HTMLElementTagNameMap {
    "rs-mold-protection": RsMoldProtection;
  }
}
