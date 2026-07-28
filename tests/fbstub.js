// Minimal in-memory Firestore compat stub, faithful enough to reproduce real
// undefined-value throw behavior and FieldValue sentinel identity checks.
(function () {
  // v10.180 ota a statisztika-kollekciok ket peldanyban leteznek: eles modban
  // 'live_' prefixszel, teszt modban prefix nelkul. A tesztek a prefix nelkuli
  // neveket toltik fel, ezert alapertelmezesben teszt modba allunk — kulonben
  // minden seed melle irna. Amelyik teszt maga akar donteni (testdb_test),
  // az a stub UTAN allitja at.
  try { localStorage.setItem('boh_testdb', '1'); } catch (e) {}
  class FieldValue {
    constructor(kind, arg) { this._kind = kind; this._arg = arg; }
  }
  function isPlainObj(v) { return !!v && typeof v === 'object' && !(v instanceof FieldValue) && !Array.isArray(v); }
  // FONTOS (valódi Firestore-viselkedés): set() a kulcsokat SZÓ SZERINTI mezőnévnek veszi
  // (a pont is a névbe kerül), csak az update() értelmezi a pontot mezőútként.
  function mergeInto(existing, incoming) {
    const out = { ...existing };
    for (const k in incoming) {
      const v = incoming[k];
      if (v instanceof FieldValue) {
        if (v._kind === 'delete') { delete out[k]; }
        else if (v._kind === 'increment') { out[k] = (out[k] || 0) + v._arg; }
        else if (v._kind === 'serverTimestamp') { out[k] = Date.now(); }
        else if (v._kind === 'arrayUnion') { out[k] = Array.from(new Set([...(out[k]||[]), ...v._arg])); }
        else if (v._kind === 'arrayRemove') { out[k] = (out[k]||[]).filter(x => !v._arg.includes(x)); }
        else { out[k] = v; }
      } else if (isPlainObj(v)) {
        out[k] = mergeInto(isPlainObj(out[k]) ? out[k] : {}, v);
      } else {
        out[k] = v;
      }
    }
    return out;
  }
  function expandPaths(incoming) {
    const out = {};
    for (const k in incoming) {
      if (!k.includes('.')) { out[k] = incoming[k]; continue; }
      const parts = k.split('.');
      let node = out;
      for (let i = 0; i < parts.length - 1; i++) {
        if (!isPlainObj(node[parts[i]])) node[parts[i]] = {};
        node = node[parts[i]];
      }
      node[parts[parts.length - 1]] = incoming[k];
    }
    return out;
  }
  function applyFieldValues(existing, incoming) { return mergeInto(existing, incoming); }
  // FONTOS (valódi Firestore-viselkedés): update() minden mezőút értékét CSERÉLI,
  // nem fésüli mélyen össze a meglévő map-pel — csak a set({merge:true}) fésül.
  function applyUpdate(existing, incoming) {
    const out = { ...existing };
    for (const k in incoming) {
      const parts = k.split('.');
      let node = out;
      for (let i = 0; i < parts.length - 1; i++) {
        const seg = parts[i];
        node[seg] = isPlainObj(node[seg]) ? { ...node[seg] } : {};
        node = node[seg];
      }
      const last = parts[parts.length - 1];
      const v = incoming[k];
      if (v instanceof FieldValue) {
        if (v._kind === 'delete') { delete node[last]; }
        else if (v._kind === 'increment') { node[last] = (node[last] || 0) + v._arg; }
        else if (v._kind === 'serverTimestamp') { node[last] = Date.now(); }
        else if (v._kind === 'arrayUnion') { node[last] = Array.from(new Set([...(node[last]||[]), ...v._arg])); }
        else if (v._kind === 'arrayRemove') { node[last] = (node[last]||[]).filter(x => !v._arg.includes(x)); }
        else { node[last] = v; }
      } else {
        node[last] = v;
      }
    }
    return out;
  }
  function assertNoUndefined(obj, path) {
    if (obj === undefined) throw new Error('FIRESTORE_UNDEFINED_VALUE at ' + (path || 'root'));
    if (obj === null || typeof obj !== 'object' || obj instanceof FieldValue) return;
    if (Array.isArray(obj)) { obj.forEach((v, i) => assertNoUndefined(v, (path||'') + '[' + i + ']')); return; }
    Object.keys(obj).forEach(k => assertNoUndefined(obj[k], (path?path+'.':'')+k));
  }

  const store = {}; // collectionPath -> { docId -> data }
  const listeners = {}; // collectionPath -> [cb] , and 'coll/doc' -> [cb]
  function notify(key) {
    (listeners[key] || []).forEach(cb => cb());
  }
  function genId() { return 'id_' + Math.random().toString(36).slice(2, 10); }

  function docRef(collPath, id) {
    if (!store[collPath]) store[collPath] = {};
    return {
      id,
      get: () => Promise.resolve({
        exists: store[collPath][id] !== undefined,
        id,
        data: () => store[collPath][id] ? { ...store[collPath][id] } : undefined,
        ref: docRef(collPath, id),
      }),
      set: (data, opts) => {
        assertNoUndefined(data);
        const existing = (opts && opts.merge) ? (store[collPath][id] || {}) : {};
        store[collPath][id] = applyFieldValues(existing, data);
        notify(collPath); notify(collPath + '/' + id);
        return Promise.resolve();
      },
      update: (data) => {
        assertNoUndefined(data);
        if (!store[collPath][id]) return Promise.reject(new Error('not-found'));
        store[collPath][id] = applyUpdate(store[collPath][id], data);
        notify(collPath); notify(collPath + '/' + id);
        return Promise.resolve();
      },
      delete: () => {
        delete store[collPath][id];
        notify(collPath); notify(collPath + '/' + id);
        return Promise.resolve();
      },
      onSnapshot: (cb) => {
        const key = collPath + '/' + id;
        const fire = () => cb({
          exists: store[collPath][id] !== undefined,
          id,
          data: () => store[collPath][id] ? { ...store[collPath][id] } : undefined,
        });
        listeners[key] = listeners[key] || [];
        listeners[key].push(fire);
        fire();
        return () => { listeners[key] = listeners[key].filter(f => f !== fire); };
      },
      collection: (sub) => collRef(collPath + '/' + id + '/' + sub),
    };
  }
  function collRef(collPath) {
    if (!store[collPath]) store[collPath] = {};
    return {
      // a valodi CollectionReference is ismeri — igy megkerdezheto, hova mutat
      path: collPath,
      id: collPath.split('/').pop(),
      doc: (id) => docRef(collPath, id || genId()),
      add: (data) => {
        assertNoUndefined(data);
        const id = genId();
        store[collPath][id] = { ...data };
        notify(collPath);
        return Promise.resolve(docRef(collPath, id));
      },
      get: () => Promise.resolve({
        empty: Object.keys(store[collPath]).length === 0,
        docs: Object.keys(store[collPath]).map(id => ({
          id, data: () => ({ ...store[collPath][id] }), ref: docRef(collPath, id),
        })),
      }),
      orderBy: () => collRef(collPath),
      limit: () => collRef(collPath),
      onSnapshot: (cb) => {
        let prevIds = new Set();
        const fire = () => {
          const ids = Object.keys(store[collPath]);
          const idSet = new Set(ids);
          const changes = [];
          ids.forEach(id => { if (!prevIds.has(id)) changes.push({ type: 'added', doc: { id, data: () => ({ ...store[collPath][id] }) } }); });
          prevIds = idSet;
          cb({
            empty: ids.length === 0,
            docs: ids.map(id => ({
              id, data: () => ({ ...store[collPath][id] }), ref: docRef(collPath, id),
            })),
            docChanges: () => changes,
          });
        };
        listeners[collPath] = listeners[collPath] || [];
        listeners[collPath].push(fire);
        fire();
        return () => { listeners[collPath] = listeners[collPath].filter(f => f !== fire); };
      },
    };
  }

  const firestoreFn = function () {
    return {
      collection: (name) => collRef(name),
      enableNetwork: () => Promise.resolve(),
      settings: () => {},
      enablePersistence: () => Promise.resolve(),
      batch: () => ({ set(){}, update(){}, delete(){}, commit: () => Promise.resolve() }),
    };
  };
  firestoreFn.FieldValue = FieldValue;
  firestoreFn.FieldValue.serverTimestamp = () => new FieldValue('serverTimestamp');
  firestoreFn.FieldValue.increment = (n) => new FieldValue('increment', n);
  firestoreFn.FieldValue.arrayUnion = (...a) => new FieldValue('arrayUnion', a);
  firestoreFn.FieldValue.arrayRemove = (...a) => new FieldValue('arrayRemove', a);
  firestoreFn.FieldValue.delete = () => new FieldValue('delete');

  window.firebase = {
    initializeApp: () => {},
    firestore: firestoreFn,
  };
  window.__fbStore = store; // expose for test inspection
})();
