import React from "react";

export default function WeatherTable({ data, onSelect }) {
  return (
    <table className="table" role="table">
      <thead>
        <tr>
          <th>City</th>
          <th>Temperature (°C)</th>
          <th>Wind (km/h)</th>
          <th>Mood</th>
          <th>Summary</th>
        </tr>
      </thead>
      <tbody>
        {data.map((r) => (
          <tr key={r.city}>
            <td>
              <button className="city-button" onClick={() => onSelect(r.city)}>
                {r.city}
              </button>
            </td>

            <td>{r.temperature ?? "-"}</td>
            <td>{r.wind_speed ?? "-"}</td>

            <td>
              <span className={`mood-tag ${moodClass(r.mood)}`}>
                {r.mood || "-"}
              </span>
            </td>

            <td className="summary">
              {formatSummary(r.summary)}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

/* ---- Helper Functions ---- */

function formatSummary(text) {
  if (!text) return "-";

  let s = text
    .replace(/\*\*/g, "")           // remove markdown bold
    .replace(/\d+\.\s*/g, "")       // remove numbering
    .replace(/\s+/g, " ")           // compress spaces
    .trim();

  if (s.length > 120) return s.slice(0, 120) + "…";

  return s;
}

function moodClass(m) {
  if (!m) return "mood-neutral";

  const mood = m.toLowerCase();

  if (mood.includes("calm") || mood.includes("relax")) return "mood-calm";
  if (mood.includes("warm") || mood.includes("hot")) return "mood-warm";
  if (mood.includes("cold") || mood.includes("chill")) return "mood-chilly";
  if (mood.includes("harsh")) return "mood-harsh";
  if (mood.includes("refresh")) return "mood-refreshing";
  if (mood.includes("gloom")) return "mood-gloomy";

  return "mood-neutral";
}
