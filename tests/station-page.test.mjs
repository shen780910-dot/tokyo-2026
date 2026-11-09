import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import vm from 'node:vm';
const ctx={window:{}};vm.createContext(ctx);for(const file of ['trip-utils','trip-data','shopping-data'])vm.runInContext(readFileSync(new URL('../assets/'+file+'.js',import.meta.url),'utf8'),ctx);
test('station shopping has its own direct route and all 19 shops have picture recommendations',()=>{
 assert.equal(ctx.window.TripUtils.resolvePage('#station'),'station');
 const items=ctx.window.SHOPPING_LIST.flatMap(x=>x.items).filter(x=>x.routeFloor&&x.decision!=='不買');
 assert.equal(new Set(items.map(x=>x.routeOrder)).size,19);
 for(const item of items){assert.ok(item.recommendation);assert.ok(item.selectionNote);assert.ok(existsSync(new URL('../'+item.image,import.meta.url)),item.id);assert.ok(item.url);}
});
test('all 40 itinerary stops are concise bullet lists and eel lunch fallback remains',()=>{
 const stops=ctx.window.TRIP.days.flatMap(x=>x.schedule);assert.equal(stops.length,40);
 for(const item of stops){assert.ok(item.points.length);for(const point of item.points)assert.ok(point.length<110,point);}
 assert.ok(stops.some(x=>x.points.some(p=>p.includes('備長'))));
});
