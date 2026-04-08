import { mount } from 'svelte'
import './app.css'
import Landing from './LandingView.svelte'

const landing = mount(Landing, {
  target: document.getElementById('app'),
})

export default landing
