<script>
  import { onMount } from 'svelte'
  export let onBack

  let currentDate = new Date()
  let events = []
  let error = null
  let selectedDay = null
  let newTitle = ''
  let newDescription = ''

  async function fetchEvents() {
    try {
      const res = await fetch('/api/calendar')
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
      const body = await res.json()
      // Expect body.items = [{id,title,date,description}]
      events = (body.items || []).map(it => ({ ...it, date: it.date }))
      error = null
    } catch (e) {
      events = []
      error = e.message
    }
  }

  onMount(() => {
    fetchEvents()
  })

  function getDaysInMonth(date) {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate()
  }

  function getFirstDayOfMonth(date) {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay()
  }

  function previousMonth() {
    currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() - 1)
  }

  function nextMonth() {
    currentDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1)
  }

  function goToToday() {
    currentDate = new Date()
  }

  $: daysInMonth = getDaysInMonth(currentDate)
  $: firstDay = getFirstDayOfMonth(currentDate)
  $: days = Array.from({ length: daysInMonth }, (_, i) => i + 1)
  $: monthName = currentDate.toLocaleString('default', { month: 'long', year: 'numeric' })

  function pad(n){ return n.toString().padStart(2,'0') }
  $: year = currentDate.getFullYear()
  $: month = (currentDate.getMonth() + 1)

  function dateKeyFor(day){
    return `${year}-${pad(month)}-${pad(day)}`
  }

  async function createEventFor(day){
    const dateStr = dateKeyFor(day)
    if (!newTitle || !newTitle.trim()) return
    try{
      const res = await fetch('/api/calendar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitle, date: dateStr, description: newDescription })
      })
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
      // refresh events and clear form
      await fetchEvents()
      newTitle = ''
      newDescription = ''
      selectedDay = null
    }catch(e){
      console.error('Create event error', e)
      alert('Failed to create event: ' + e.message)
    }
  }

  function openDay(day){
    selectedDay = selectedDay === day ? null : day
    // reset form when opening
    if (selectedDay === day) {
      newTitle = ''
      newDescription = ''
    }
  }

  // Map events by ISO date string YYYY-MM-DD for quick lookup
  $: eventsByDate = events.reduce((acc, ev) => {
    if (!ev.date) return acc
    const key = ev.date.split('T')[0] // handle possible datetime
    acc[key] = acc[key] || []
    acc[key].push(ev)
    return acc
  }, {})
</script>

<main>
  <div class="header">
    <button class="back-btn" on:click={onBack}>← Back</button>
    <h1>Calendar</h1>
  </div>

  <div class="calendar-container">
    <div class="calendar-controls">
      <button on:click={previousMonth}>←</button>
      <span class="month-name">{monthName}</span>
      <button on:click={nextMonth}>→</button>
      <button on:click={goToToday} class="today-btn">Today</button>
    </div>
    <div class="calendar-grid">
      <div class="weekday">Sun</div>
      <div class="weekday">Mon</div>
      <div class="weekday">Tue</div>
      <div class="weekday">Wed</div>
      <div class="weekday">Thu</div>
      <div class="weekday">Fri</div>
      <div class="weekday">Sat</div>
      
      {#each Array(firstDay) as _}
        <div class="empty"></div>
      {/each}
      
      {#each days as day}
        <div class="day" on:click={() => openDay(day)}>
          <div class="day-number">{day}</div>
          {#if eventsByDate[dateKeyFor(day)]}
            <div class="events">
              {#each eventsByDate[dateKeyFor(day)] as ev}
                <div class="event-badge" title={ev.description}>{ev.title}</div>
              {/each}
            </div>
          {/if}

          {#if selectedDay === day}
            <form class="event-form" on:submit|preventDefault={() => createEventFor(day)} on:click|stopPropagation>
              <input placeholder="Title" bind:value={newTitle} required />
              <input placeholder="Description" bind:value={newDescription} />
              <div class="form-actions">
                <button type="submit">Add</button>
                <button type="button" on:click={() => (selectedDay = null)}>Cancel</button>
              </div>
            </form>
          {/if}
        </div>
      {/each}
    </div>
  </div>
</main>

<style>
  main {
    padding: 2rem;
    max-width: 900px;
    margin: 0 auto;
  }

  .header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
  }

  .back-btn {
    padding: 0.5rem 1rem;
    background: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  .back-btn:hover {
    background: #e0e0e0;
  }

  h1 {
    margin: 0;
  }

  .calendar-container {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .calendar-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 2rem;
    gap: 1rem;
  }

  .calendar-controls button {
    background: #f0f0f0;
    border: 1px solid #ddd;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
  }

  .calendar-controls button:hover {
    background: #e0e0e0;
  }

  .calendar-controls .today-btn {
    background: #007bff;
    color: white;
    border: none;
  }

  .calendar-controls .today-btn:hover {
    background: #0056b3;
  }

  .month-name {
    font-weight: bold;
    min-width: 150px;
    text-align: center;
  }

  .calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 0.5rem;
  }

  .weekday {
    font-weight: bold;
    text-align: center;
    padding: 0.75rem;
    font-size: 0.9rem;
    color: #666;
  }

  .day {
    aspect-ratio: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem;
    border: 1px solid #eee;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
    flex-direction: column;
    align-items: flex-start;
  }

  .day:hover {
    background: #f0f0f0;
    border-color: #007bff;
  }

  .empty {
    aspect-ratio: 1;
  }

  .day-number {
    font-weight: 600;
    margin-bottom: 0.25rem;
    width: 100%;
    text-align: left;
  }

  .events {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    width: 100%;
  }

  .event-badge {
    background: #007bff;
    color: white;
    padding: 0.15rem 0.4rem;
    border-radius: 4px;
    font-size: 0.75rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .event-form {
    margin-top: 0.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    width: 100%;
  }

  .event-form input {
    padding: 0.35rem 0.5rem;
    border-radius: 4px;
    border: 1px solid #ddd;
    font-size: 0.85rem;
    width: 100%;
  }

  .form-actions {
    display: flex;
    gap: 0.5rem;
    justify-content: flex-end;
  }

  .form-actions button {
    padding: 0.35rem 0.6rem;
    border-radius: 4px;
    border: none;
    cursor: pointer;
  }

  .form-actions button[type="submit"] {
    background: #007bff;
    color: white;
  }

  .form-actions button[type="button"] {
    background: #f0f0f0;
  }
</style>
