import { mount } from 'svelte'
import './app.css'
import Calendar from './CalendarView.svelte'

const calendar = mount(Calendar, {
  target: document.getElementById('app'),
})

export default app
