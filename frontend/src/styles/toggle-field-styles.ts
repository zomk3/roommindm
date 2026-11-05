import { css } from "lit";

/**
 * Toggle rows (icon + title + description, switch on the right) and number fields with
 * hints, as used by the settings pages. Shared so room settings look the same.
 */
export const toggleFieldStyles = css`
  .toggle-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
  }
  .toggle-text {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
  }
  .toggle-label {
    font-size: 14px;
    font-weight: 500;
    color: var(--primary-text-color);
  }
  .toggle-label ha-icon {
    --mdc-icon-size: 18px;
    vertical-align: middle;
    margin-right: 4px;
  }
  .toggle-hint {
    font-size: 13px;
    color: var(--secondary-text-color);
    line-height: 1.4;
  }
  ha-switch {
    flex-shrink: 0;
  }

  .threshold-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .threshold-grid.three {
    grid-template-columns: 1fr 1fr 1fr;
  }
  .threshold-field {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .threshold-field ha-textfield {
    width: 100%;
  }
  .field-hint {
    color: var(--secondary-text-color);
    font-size: 12px;
  }

  @media (max-width: 600px) {
    .threshold-grid,
    .threshold-grid.three {
      grid-template-columns: 1fr;
    }
  }
`;
