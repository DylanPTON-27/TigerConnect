import { mount } from 'svelte'
import './app.css'
import StatusView from './StatusView.svelte'

const landing = mount(StatusView, {
  target: document.getElementById('app'),
})

export default landing
