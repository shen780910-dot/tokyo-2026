window.TripUtils = {
  resolvePage(hash) { const page=hash.replace(/^#/, ''); return /^day-[1-4]$/.test(page)?'itinerary':['overview','itinerary','prep'].includes(page)?page:'overview'; },
  resolveDay(hash) { const match=/^#day-([1-4])$/.exec(hash); return match?Number(match[1])-1:0; },
  isNavigationLink(url) { return /^https?:\/\/(?:www\.)?google\.[^/]+\/maps(?:\/|\?|$)/i.test(url)||/^https?:\/\/(?:maps\.app\.goo\.gl|goo\.gl\/maps)/i.test(url); },
  createSafeStorage(storage) {
    const memory=new Map();
    return {get(key,fallback=null){if(memory.has(key))return memory.get(key);try{return storage?.getItem(key)??fallback;}catch{return fallback;}},set(key,value){memory.set(key,value);try{storage?.setItem(key,value);}catch{}}};
  }
};
