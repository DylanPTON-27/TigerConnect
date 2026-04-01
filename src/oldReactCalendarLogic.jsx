import ICAL from 'ical.js';

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