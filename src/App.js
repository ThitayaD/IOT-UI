import React, { useState, useEffect } from 'react';
import './App.css';

function getFormattedDate() {
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const now = new Date();

  const day = days[now.getDay()];
  const month = months[now.getMonth()];
  const date = now.getDate();

  return `${day}, ${month} ${date}`;
}

function App() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [currentTemp, setTemp] = useState(0);
  const [currentRain, setRain] = useState(0);
  const [currentLocale, setLocale] = useState('Bangkok');
  const [currentMsg, setMsg] = useState('No rain warning');
  const [busData, setBusData] = useState([]);



  const fetchData = () => {
    // if (navigator.geolocation) {
    //   navigator.geolocation.getCurrentPosition((position) => {
    //     const { latitude, longitude } = position.coords;
    // fetch(`/temp?lat=${latitude}&lng=${longitude}`)
    fetch(`/temp`)
      .then(res => res.json())
      .then(data => {
        setTemp(data.temp);
      });
    // fetch(`/rain?lat=${latitude}&lng=${longitude}`)        
    fetch(`/rain`)
      .then(res => res.json())
      .then(data => {
        setRain(data.percip);
        setLocale(data.location);
        setMsg(data.msg);
      });
  };


  const fetchBusData = () => {
    fetch("/bus")
      .then((res) => res.json())
      .then((data) => {
        const existingBus = busData.find((bus) => bus.Bus_No === data.Bus_No);
        if (!existingBus) {
          setBusData((prevData) => [...prevData, { ...data, id: Date.now() }]); // Assign a unique id
        } else {
          if (data.ETA < existingBus.ETA) {
            setBusData((prevData) =>
              prevData.map((bus) =>
                bus.Bus_No === data.Bus_No ? { ...bus, ETA: data.ETA } : bus
              )
            );
          }
        }
      });
  };

  useEffect(() => {
    fetchBusData();
    const interval = setInterval(() => {
      fetchBusData();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(new Date());
      setBusData((prevData) =>
        prevData.map((bus) => ({
          ...bus,
          ETA: bus.ETA > 0 ? bus.ETA - 1 : bus.ETA === "Soon" ? "Soon" : 0,
        }))
      );

      // Remove buses with ETA 0 or "Soon"
      setBusData((prevData) => prevData.filter((bus) => bus.ETA !== 0 && bus.ETA !== "Soon"));

      // Check if any bus has reached 1 minute
      const busesAtOneMinute = busData.filter((bus) => bus.ETA === 1);

      if (busesAtOneMinute.length > 0) {
        busesAtOneMinute.forEach((bus) => {
          const data = JSON.stringify({ "Bus_No": bus.Bus_No, "Destination": bus.Destination });

          // Send data using sendBeacon
          navigator.sendBeacon('/tts', data);
        });
      }
    }, 5000); // Update time and remove completed buses every minute

    return () => clearInterval(interval);
  }, [busData]);


  useEffect(() => {
    fetchData(); // Fetch data once before starting the interval

    const interval = setInterval(() => {
      fetchData(); // Fetch data at intervals
    }, 3600000); // Change to 1 hour in the real app

    return () => clearInterval(interval);
  }, []);
  // ... rest of the code remains the same

  const options = { hour: '2-digit', minute: '2-digit', hour12: false };
  const formattedTime = currentTime.toLocaleTimeString('en-US', options);

  return (
    <div className="App">
      <header className="App-header">
        <div className="app-container">
          <div className="block left-block">
            <div className="icons">
              {/* Add icons here */}
            </div>
            <div className="box-container">
              <div className="box top">
                <p className='box-text-time'>{formattedTime}</p>
                <p className='box-text-date'>{getFormattedDate()}</p>

              </div>
              <div className="box">
                <img className="bus-location" alt="" src="/BUS_LOCATION.png" />
              </div>
              <div className="box bottom">
                <p className='box-text'>{currentLocale}</p>
                <p className='box-text-temp'>{currentTemp}°</p>
                <p className='box-text-msg'>{currentMsg}</p>
              </div>
            </div>
          </div>
          <div className="block right-block">
            <div className="section bus">
              <div className="bus-table-container">
                <table className="bus-table">
                  <thead>
                    <tr className="header-wrapper">
                      <th>Route</th>
                      <th>Destination</th>
                      <th>Arrival</th>
                    </tr>
                  </thead>
                  <tbody>
                    {busData.slice(0, 5).map((bus, index) => ( // <-- Added an 'index' parameter
                      <tr key={`${bus.Bus_No}-${bus.Destination}-${index}`} className='child-wrapper'>
                        <td>{bus.Bus_No}</td>
                        <td>{bus.Destination}</td>
                        <td>{bus.ETA === 0 ? "Soon" : bus.ETA === "Soon" ? bus.ETA : bus.ETA + " min"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;