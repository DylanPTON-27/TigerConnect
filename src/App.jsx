import { useState, useEffect } from 'react'
import './App.css'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import iCalendarPlugin from '@fullcalendar/icalendar'; 
import ICAL from 'ical.js';
import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import Header from './components/Header'

function App() {
  const [currentTime, setCurrentTime] = useState(0);

  useEffect(() => {
    fetch('/api/time').then(res => res.json()).then(data => {
      setCurrentTime(data.time);
    });
  }, []);

  const [events, setEvents] = useState([]);

  useEffect(() => {
    async function loadIcsFromApi() {
      try {
        const response = await fetch('/api/calendar');
        const icsString = await response.text();
        
        // Use ical.js to parse the string
        const jcalData = ICAL.parse(icsString);
        const comp = new ICAL.Component(jcalData);
        const vevents = comp.getAllSubcomponents('vevent');

        // Map them to FullCalendar event objects
        const mappedEvents = vevents.map(vevent => {
          const event = new ICAL.Event(vevent);
          return {
            title: event.summary,
            start: event.startDate.toJSDate(),
            end: event.endDate.toJSDate(),
            description: event.description
          };
        });

        setEvents(mappedEvents);
      } catch (error) {
        console.error("Failed to fetch ICS:", error);
      }
    }

    loadIcsFromApi();
  }, []);

  const VisuallyHiddenInput = styled('input')({
    clip: 'rect(0 0 0 0)',
    clipPath: 'inset(50%)',
    height: 1,
    overflow: 'hidden',
    position: 'absolute',
    bottom: 0,
    left: 0,
    whiteSpace: 'nowrap',
    width: 1,
  });

  const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(
        '/api/upload',
        {
          method: 'POST',
          body: formData
        }
      );

      if (response.ok) {
        console.log(response.status);
      }
      window.location.reload(true); 
    
    } catch (error) {
      console.log(error);
    }
  };

  return (
    <>
      <Header />
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>TigerConnect</h1>

      <FullCalendar
        plugins={[dayGridPlugin, iCalendarPlugin]}
        height={400}
        initialView="dayGridMonth"
        events={events}
      />

      <br/>

      <Button
        component="label"
        role={undefined}
        variant="contained"
        tabIndex={-1}
        startIcon={<CloudUploadIcon />}
      >
        Upload files
        <VisuallyHiddenInput
          type="file"
          onChange={(event) => uploadFile(event.target.files[0])}
          single
        />
      </Button>


      <div className="card">

        <p>The current time is {new Date(currentTime * 1000).toLocaleString()}.</p>
        
      </div>
      <p className="read-the-docs">
        TigerConnect is currently in development.
      </p>
    </>
  )
}

export default App