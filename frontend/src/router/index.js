import { createRouter, createWebHistory } from 'vue-router'
import VideoList from '../views/VideoList.vue'
import VideoPlayer from '../views/VideoPlayer.vue'
import Profile from '../views/Profile.vue'
import Favorites from '../views/Favorites.vue'

const routes = [
  {
    path: '/',
    name: 'VideoList',
    component: VideoList
  },
  {
    path: '/player/:id',
    name: 'Player',
    component: VideoPlayer,
    props: true
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: Favorites
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router