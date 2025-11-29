import React from "react";

export default function CityDetail({ record, onClose }) {
  if (!record) return null;
  return (
    <div style={{
      position: "fixed",
      left: 0, right:0, top:0, bottom:0,
      background: "rgba(0,0,0,0.4)",
      display: "flex", justifyContent:"center", alignItems:"center"
    }}>
      <div style={{ width: "720px", background:"#fff", padding:20, borderRadius:8 }}>
        <div style={{ display:"flex", justifyContent:"space-between", marginBottom:12 }}>
          <h3>{record.city}</h3>
          <button onClick={onClose}>Close</button>
        </div>
        <pre style={{ whiteSpace:"pre-wrap", maxHeight: "60vh", overflow: "auto" }}>
          {JSON.stringify(record, null, 2)}
        </pre>
      </div>
    </div>
  );
}
