window.TripUtils = {
  resolvePage(hash) { const page=hash.replace(/^#/, ''); return ['overview','itinerary','prep'].includes(page)?page:'overview'; },
  createSafeStorage(storage) {
    const memory=new Map();
    return {get(key,fallback=null){if(memory.has(key))return memory.get(key);try{return storage?.getItem(key)??fallback;}catch{return fallback;}},set(key,value){memory.set(key,value);try{storage?.setItem(key,value);}catch{}}};
  }
};
