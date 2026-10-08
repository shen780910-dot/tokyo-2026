import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const sandbox={window:{}};vm.createContext(sandbox);
for(const name of ['trip-utils.js','trip-data.js']){const p=new URL('../assets/'+name,import.meta.url);if(fs.existsSync(p))vm.runInContext(fs.readFileSync(p,'utf8'),sandbox);}
test('routing excludes unconfirmed sections',()=>{const u=sandbox.window.TripUtils;assert.ok(u);assert.equal(u.resolvePage('#itinerary'),'itinerary');for(const h of ['#stay','#rental','#missing'])assert.equal(u.resolvePage(h),'overview');});
test('blocked storage preserves session choices',()=>{const u=sandbox.window.TripUtils;assert.ok(u);const s=u.createSafeStorage({getItem(){throw Error();},setItem(){throw Error();}});s.set('theme','dark');assert.equal(s.get('theme'),'dark');assert.equal(s.get('unknown','light'),'light');});
test('published data contains four proposed days and no stay or rental records',()=>{const t=sandbox.window.TRIP;assert.ok(t);assert.equal(t.days.length,4);assert.equal(t.adults,2);assert.equal(t.children,1);assert.equal(t.stays,undefined);assert.equal(t.rentals,undefined);assert.equal(t.days.every(x=>x.status==='proposed'),true);});
