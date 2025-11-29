import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "https://weather-api-144535994725.us-central1.run.app";

export async function fetchAllWeather(authToken = null) {
  const headers = authToken
    ? { Authorization: `Bearer ${authToken}` }
    : {};

  const resp = await axios.get(`${API_URL}/weather/all`, { headers });
  return resp.data;
}

export async function fetchCityWeather(city, authToken = null) {
  const headers = authToken
    ? { Authorization: `Bearer ${authToken}` }
    : {};

  const resp = await axios.get(
    `${API_URL}/weather/${encodeURIComponent(city)}`,
    { headers }
  );
  return resp.data;
}
