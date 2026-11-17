/**
 * rs-mold-protection – a room's mold protection: prevention heating, the airing hint and the
 * dehumidifier.
 *
 * Lives in the room's own "Mold protection" card. The dehumidifier device and its tank sensor
 * are chosen under Devices, the humidity sensor under Sensors.
 */
import { LitElement, html, css, nothing } from "lit";
import { customElement, property } from "lit/decorators.js";
import type { HomeAssistant } from "../types";
import { localize } from "../utils/localize";
import { tokens } from "../styles/tokens";
import "./shared/rs-list-row";
import "./shared/rs-number-field";

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
  @property({ type: Boolean }) public ventilationHintEnabled = true;

  static styles = [
    tokens,
    css`
      :host {
        display: block;
      }
      .bounds {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--rs-space-4);
        margin-top: var(--rs-space-3);
      }
      @media (max-width: 420px) {
        .bounds {
          grid-template-columns: 1fr;
        }
      }
    `,
  ];

  render() {
    const l = this.hass.language;
    return this.editing ? this._renderEdit(l) : this._renderView(l);
  }

  private _renderView(l: string) {
    const name =
      (this.hass.states[this.dehumidifierEntity]?.attributes?.friendly_name as string) ||
      this.dehumidifierEntity;
    return html`
      <rs-list-row
        clickable
        chevron
        icon="mdi:shield-check"
        .heading=${localize("mold.room_heating_title", l)}
        .value=${localize(this.moldPreventionHeating ? "common.on" : "common.off", l)}
        @row-click=${this._fireEdit}
      ></rs-list-row>
      ${
        this.humiditySensor
          ? html`<rs-list-row
              clickable
              chevron
              icon="mdi:window-open-variant"
              .heading=${localize("mold.room_ventilation_title", l)}
              .secondary=${this.ventilationHintEnabled ? `≥ ${this.dehumidifierUpper} %` : ""}
              .value=${localize(this.ventilationHintEnabled ? "common.on" : "common.off", l)}
              @row-click=${this._fireEdit}
            ></rs-list-row>`
          : nothing
      }
      ${
        this.dehumidifierEntity
          ? html`<rs-list-row
              clickable
              chevron
              icon=${this.dehumidifierEnabled ? "mdi:air-humidifier" : "mdi:air-humidifier-off"}
              .heading=${localize("dehumidifier.enabled", l)}
              .secondary=${
                this.dehumidifierEnabled
                  ? `${name} · ${this.dehumidifierLower}–${this.dehumidifierUpper} %`
                  : ""
              }
              .value=${localize(this.dehumidifierEnabled ? "common.on" : "common.off", l)}
              @row-click=${this._fireEdit}
            ></rs-list-row>`
          : nothing
      }
    `;
  }

  private _renderEdit(l: string) {
    const dehumidifierReady = !!this.dehumidifierEntity && !!this.humiditySensor;
    return html`
      <rs-list-row
        switch
        wrap
        icon="mdi:shield-check"
        .heading=${localize("mold.room_heating_title", l)}
        .secondary=${localize("mold.room_heating_hint", l)}
        .checked=${this.moldPreventionHeating}
        @toggle-changed=${(e: CustomEvent<boolean>) => {
          e.stopPropagation();
          this._fire("mold_prevention_heating", e.detail);
        }}
      ></rs-list-row>
      <rs-list-row
        switch
        wrap
        icon="mdi:window-open-variant"
        .heading=${localize("mold.room_ventilation_title", l)}
        .secondary=${localize(
          this.humiditySensor ? "mold.room_ventilation_hint" : "mold.room_ventilation_requires",
          l,
        )}
        .checked=${this.ventilationHintEnabled && !!this.humiditySensor}
        .disabled=${!this.humiditySensor}
        @toggle-changed=${(e: CustomEvent<boolean>) => {
          e.stopPropagation();
          this._fire("ventilation_hint_enabled", e.detail);
        }}
      ></rs-list-row>
      <rs-list-row
        switch
        wrap
        icon="mdi:air-humidifier"
        .heading=${localize("dehumidifier.enabled", l)}
        .secondary=${localize(dehumidifierReady ? "dehumidifier.hint" : "dehumidifier.requires", l)}
        .checked=${this.dehumidifierEnabled}
        .disabled=${!dehumidifierReady}
        @toggle-changed=${(e: CustomEvent<boolean>) => {
          e.stopPropagation();
          this._fire("dehumidifier_enabled", e.detail);
        }}
      ></rs-list-row>
      ${
        this.dehumidifierEnabled || (this.ventilationHintEnabled && this.humiditySensor)
          ? html`<div class="bounds">
              ${
                this.dehumidifierEnabled
                  ? html`<rs-number-field
                      .label=${localize("dehumidifier.lower", l)}
                      suffix="%"
                      .min=${1}
                      .max=${this.dehumidifierUpper - 1}
                      .step=${1}
                      .value=${this.dehumidifierLower}
                      @value-changed=${(e: CustomEvent<{ value: number }>) =>
                        this._fire("dehumidifier_lower_bound", e.detail.value)}
                    ></rs-number-field>`
                  : nothing
              }
              <rs-number-field
                .label=${localize(
                  this.dehumidifierEnabled ? "dehumidifier.upper" : "mold.room_ventilation_upper",
                  l,
                )}
                suffix="%"
                .min=${this.dehumidifierLower + 1}
                .max=${100}
                .step=${1}
                .value=${this.dehumidifierUpper}
                @value-changed=${(e: CustomEvent<{ value: number }>) =>
                  this._fire("dehumidifier_upper_bound", e.detail.value)}
              ></rs-number-field>
            </div>`
          : nothing
      }
    `;
  }

  private _fireEdit(e: Event) {
    e.stopPropagation();
    this.dispatchEvent(new CustomEvent("edit-click", { bubbles: true, composed: true }));
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
