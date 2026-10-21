import fs from 'node:fs';import vm from 'node:vm';import path from 'node:path';import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const context={window:{}};vm.runInNewContext(fs.readFileSync(path.join(root,'assets/shopping-data.js'),'utf8'),context);
const ids=context.window.SHOPPING_LIST.flatMap(group=>group.items.map(item=>item.id));
if(new Set(ids).size!==ids.length||ids.some(id=>!/^[-a-zA-Z0-9_]+$/.test(id)))throw Error('Invalid or duplicated shopping IDs');
const target=process.argv[2];if(target)fs.writeFileSync(path.resolve(target),JSON.stringify(ids,null,2)+'\n');else console.log(JSON.stringify(ids));
