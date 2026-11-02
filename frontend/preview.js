import { LitElement, html, css } from 'lit';

// Lightweight stand-ins for host-provided Home Assistant controls. RoomMind's
// device and sensor sections below are the production components.
class PreviewPicker extends LitElement {
  static properties = { hass: {attribute:false}, includeDomains:{attribute:false}, entityFilter:{attribute:false}, value:{}, label:{} };
  static styles = css`:host{display:block;width:100%}label{display:block;font:13px Arial;color:#9daebd;margin:12px 0}select{box-sizing:border-box;width:100%;padding:13px;margin-top:8px;border:1px solid #465969;border-radius:8px;background:#111d28;color:#e6edf4;font-size:14px}`;
  render(){const options=Object.values(this.hass?.states??{}).filter(e=>(!this.includeDomains||this.includeDomains.includes(e.entity_id.split('.')[0]))&&(!this.entityFilter||this.entityFilter(e)));return html`<label>${this.label}<select .value=${this.value??''} @change=${e=>{this.value=e.target.value;this.dispatchEvent(new CustomEvent('value-changed',{detail:{value:this.value},bubbles:true,composed:true}));}}><option value="">None</option>${options.map(e=>html`<option value=${e.entity_id} ?selected=${e.entity_id===this.value}>${e.attributes.friendly_name}</option>`)}</select></label>`;}
}
customElements.define('ha-entity-picker',PreviewPicker);
class PreviewIcon extends HTMLElement { connectedCallback(){this.setAttribute('aria-hidden','true');this.style.cssText='display:inline-block;width:18px;color:var(--primary-color)';this.textContent=this.getAttribute('icon')?.includes('water')?'◉':'◇';} }
customElements.define('ha-icon',PreviewIcon);
class PreviewCheck extends LitElement {static properties={checked:{type:Boolean},disabled:{type:Boolean}};render(){return html`<input aria-label="Select entity" type="checkbox" .checked=${!!this.checked} ?disabled=${this.disabled} @click=${e=>e.stopPropagation()} @change=${e=>{this.checked=e.target.checked;this.dispatchEvent(new CustomEvent('change',{bubbles:true,composed:true}));}}>`;}}
customElements.define('ha-checkbox',PreviewCheck);
customElements.define('ha-radio',class extends PreviewCheck{});
await import('./src/components/rs-device-section.ts');
await import('./src/components/rs-sensor-section.ts');
const states=Object.fromEntries([
 ['switch.bathroom_dehumidifier','Bathroom dehumidifier','off',{}],
 ['humidifier.portable_dehumidifier','Portable dehumidifier','off',{device_class:'dehumidifier'}],
 ['sensor.bathroom_temperature','Bathroom temperature','21.5',{device_class:'temperature',unit_of_measurement:'°C'}],
 ['sensor.bathroom_humidity','Bathroom humidity','65',{device_class:'humidity',unit_of_measurement:'%'}]
].map(([entity_id,friendly_name,state,attributes])=>[entity_id,{entity_id,state,attributes:{friendly_name,...attributes}}]));
const hass={language:'en',states,config:{unit_system:{temperature:'°C'}},entities:Object.fromEntries(Object.keys(states).map(entity_id=>[entity_id,{entity_id,area_id:'bathroom',device_id:null}])),devices:{},areas:{bathroom:{area_id:'bathroom',name:'Bathroom'}},callWS:async()=>({}),callService:async()=>({}),localize:key=>key};
const device=document.querySelector('#devices'),sensor=document.querySelector('#sensors');
for(const component of [device,sensor]){component.hass=hass;component.area=hass.areas.bathroom;component.editing=true;}
device.devices=[];
let settings;
try{settings=JSON.parse(localStorage.getItem('roommind-preview')||'null');}catch{}
settings??={dehumidifier_entity:'switch.bathroom_dehumidifier',dehumidifier_enabled:true,dehumidifier_lower_bound:50,dehumidifier_upper_bound:60,humidity_sensor:'sensor.bathroom_humidity',temperature_sensor:'sensor.bathroom_temperature'};
function sync(){device.dehumidifierEntity=sensor.dehumidifierEntity=settings.dehumidifier_entity;sensor.dehumidifierEnabled=settings.dehumidifier_enabled;sensor.dehumidifierLower=settings.dehumidifier_lower_bound;sensor.dehumidifierUpper=settings.dehumidifier_upper_bound;sensor.humiditySensor=settings.humidity_sensor;sensor.temperatureSensor=settings.temperature_sensor;}
function change(e){const {key,value}=e.detail;settings[key]=value;if((key==='dehumidifier_entity'||key==='humidity_sensor')&&!value)settings.dehumidifier_enabled=false;sync();localStorage.setItem('roommind-preview',JSON.stringify(settings));document.querySelector('#saved').textContent='Preview settings saved in this browser';}
device.addEventListener('dehumidifier-changed',change);sensor.addEventListener('sensor-changed',change);sync();
