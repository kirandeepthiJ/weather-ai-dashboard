import React, { useEffect, useState } from "react";
import { fetchAllWeather, fetchCityWeather } from "./api";
import WeatherTable from "./components/WeatherTable";
import CityDetail from "./components/CityDetail";

function App() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");

  // If API is private, you must obtain an identity token and pass it
  // For demo we support no-auth mode where REACT_APP_API_URL points to public API.
  const getAuthToken = async () => {
    // For secure calls from GKE, we'll use Workload Identity; the frontend won't get tokens.
    // If you need browser-based token (not recommended) implement OAuth flow.
    return null;
  };

  useEffect(() => {
    let mounted = true;
    (async () => {
      setLoading(true);
      setError("");
      try {
        const token = await getAuthToken();
        const resp = await fetchAllWeather(token);
        if (!mounted) return;
        setData(resp);
      } catch (e) {
        console.error(e);
        setError("Failed to fetch data. Check console.");
      } finally {
        setLoading(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const handleSelect = async (city) => {
    setLoading(true);
    try {
      const token = await getAuthToken();
      const rec = await fetchCityWeather(city, token);
      setSelected(rec);
    } catch (e) {
      setError("Failed to fetch city details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="header">
        <h2>Weather AI Dashboard</h2>
        <div>
          <small>Project: weather-ai-dashboard</small>
        </div>
      </div>

      {loading && <div>Loading...</div>}
      {error && <div style={{ color: "red" }}>{error}</div>}
      {!loading && <WeatherTable data={data} onSelect={handleSelect} />}

      <CityDetail record={selected} onClose={() => setSelected(null)} />
    </div>
  );
}

export default App;
