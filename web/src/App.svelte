<script>
  import CalendarPage from './CalendarPage.svelte'
  import ToDoListPage from './ToDoListPage.svelte'
  import ComplianceListPage from './ComplianceListPage.svelte'
  
  let currentView = 'dashboard' // 'dashboard', 'calendar', 'todolist', or 'compliance'
  let todoItems = []
  let complianceItems = []
  let newTodoText = ''
  let newComplianceText = ''
  let currentDate = new Date()

  function addTodoItem() {
    if (newTodoText.trim()) {
      todoItems = [...todoItems, { id: Date.now(), text: newTodoText, completed: false }]
      newTodoText = ''
    }
  }

  function toggleTodo(id) {
    todoItems = todoItems.map(item =>
      item.id === id ? { ...item, completed: !item.completed } : item
    )
  }

  function removeTodo(id) {
    todoItems = todoItems.filter(item => item.id !== id)
  }

  function addComplianceItem() {
    if (newComplianceText.trim()) {
      complianceItems = [...complianceItems, { id: Date.now(), text: newComplianceText, completed: false }]
      newComplianceText = ''
    }
  }

  function toggleCompliance(id) {
    complianceItems = complianceItems.map(item =>
      item.id === id ? { ...item, completed: !item.completed } : item
    )
  }

  function removeCompliance(id) {
    complianceItems = complianceItems.filter(item => item.id !== id)
  }

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
</script>

<main>
  {#if currentView === 'dashboard'}
    <h1>Dashboard</h1>
    
    <div class="widgets-container">
      <!-- Calendar Widget -->
      <div class="widgets-left">
        <div class="widget calendar-widget" on:click={() => currentView = 'calendar'} role="button" tabindex="0">
          <h2>Calendar</h2>
          <div class="calendar-controls">
            <button on:click|stopPropagation={previousMonth}>←</button>
            <span class="month-name">{monthName}</span>
            <button on:click|stopPropagation={nextMonth}>→</button>
            <button on:click|stopPropagation={goToToday} class="today-btn">Today</button>
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
              <div class="day">{day}</div>
            {/each}
          </div>
        </div>
      </div>

      <!-- Right column with stacked widgets -->
      <div class="widgets-right">
        <!-- To-Do List Widget -->
        <div class="widget" on:click={() => currentView = 'todolist'} role="button" tabindex="0">
          <h2>To-Do List</h2>
          <div class="input-group">
            <input
              type="text"
              placeholder="Add a task..."
              bind:value={newTodoText}
              on:keydown|stopPropagation={e => e.key === 'Enter' && addTodoItem()}
              on:click|stopPropagation={() => {}}
            />
            <button on:click|stopPropagation={addTodoItem}>Add</button>
          </div>
          <ul class="task-list">
            {#each todoItems as item (item.id)}
              <li on:click|stopPropagation={() => {}}>
                <input
                  type="checkbox"
                  checked={item.completed}
                  on:change|stopPropagation={() => toggleTodo(item.id)}
                />
                <span class:completed={item.completed}>{item.text}</span>
                <button on:click|stopPropagation={() => removeTodo(item.id)} class="delete-btn">×</button>
              </li>
            {/each}
          </ul>
        </div>

        <!-- Compliance Check List Widget -->
        <div class="widget" on:click={() => currentView = 'compliance'} role="button" tabindex="0">
          <h2>Compliance Check List</h2>
          <div class="input-group">
            <input
              type="text"
              placeholder="Add compliance item..."
              bind:value={newComplianceText}
              on:keydown|stopPropagation={e => e.key === 'Enter' && addComplianceItem()}
              on:click|stopPropagation={() => {}}
            />
            <button on:click|stopPropagation={addComplianceItem}>Add</button>
          </div>
          <ul class="task-list">
            {#each complianceItems as item (item.id)}
              <li on:click|stopPropagation={() => {}}>
                <input
                  type="checkbox"
                  checked={item.completed}
                  on:change|stopPropagation={() => toggleCompliance(item.id)}
                />
                <span class:completed={item.completed}>{item.text}</span>
                <button on:click|stopPropagation={() => removeCompliance(item.id)} class="delete-btn">×</button>
              </li>
            {/each}
          </ul>
        </div>
      </div>
    </div>
  {:else if currentView === 'calendar'}
    <CalendarPage onBack={() => currentView = 'dashboard'} />
  {:else if currentView === 'todolist'}
    <ToDoListPage bind:todoItems onBack={() => currentView = 'dashboard'} />
  {:else if currentView === 'compliance'}
    <ComplianceListPage bind:complianceItems onBack={() => currentView = 'dashboard'} />
  {/if}
</main>

<style>
  main {
    padding: 2rem;
    max-width: 1200px;
    margin: 0 auto;
  }

  h1 {
    margin-bottom: 2rem;
  }

  .widgets-container {
    display: flex;
    gap: 2rem;
  }

  .widgets-left {
    flex: 1.5;
  }

  .widgets-right {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .widget {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    transition: box-shadow 0.2s, transform 0.2s;
  }

  .widget:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }

  .widget h2 {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.25rem;
  }

  .calendar-widget {
    min-width: 280px;
  }

  .calendar-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
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
    flex: 1;
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
    padding: 0.5rem;
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
  }

  .day:hover {
    background: #f9f9f9;
  }

  .empty {
    aspect-ratio: 1;
  }

  .input-group {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }

  .input-group input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  .input-group button {
    padding: 0.5rem 1rem;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
  }

  .input-group button:hover {
    background: #0056b3;
  }

  .task-list {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .task-list li {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem;
    border-bottom: 1px solid #eee;
  }

  .task-list li:last-child {
    border-bottom: none;
  }

  .task-list input[type="checkbox"] {
    cursor: pointer;
    width: 18px;
    height: 18px;
  }

  .task-list span {
    flex: 1;
    word-break: break-word;
  }

  .task-list span.completed {
    text-decoration: line-through;
    color: #999;
  }

  .delete-btn {
    background: none;
    border: none;
    color: #999;
    cursor: pointer;
    font-size: 1.25rem;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .delete-btn:hover {
    color: #d9534f;
  }
</style>