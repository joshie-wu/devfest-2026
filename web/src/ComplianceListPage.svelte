<script>
  export let complianceItems = []
  export let onBack
  
  let newComplianceText = ''

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
</script>

<main>
  <div class="header">
    <button class="back-btn" on:click={onBack}>← Back</button>
    <h1>Compliance Check List</h1>
  </div>

  <div class="list-container">
    <div class="input-group">
      <input
        type="text"
        placeholder="Add compliance item..."
        bind:value={newComplianceText}
        on:keydown={e => e.key === 'Enter' && addComplianceItem()}
      />
      <button on:click={addComplianceItem}>Add</button>
    </div>
    <ul class="task-list">
      {#each complianceItems as item (item.id)}
        <li>
          <input
            type="checkbox"
            checked={item.completed}
            on:change={() => toggleCompliance(item.id)}
          />
          <span class:completed={item.completed}>{item.text}</span>
          <button on:click={() => removeCompliance(item.id)} class="delete-btn">×</button>
        </li>
      {/each}
    </ul>
  </div>
</main>

<style>
  main {
    padding: 2rem;
    max-width: 700px;
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

  .list-container {
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 2rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .input-group {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }

  .input-group input {
    flex: 1;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }

  .input-group button {
    padding: 0.75rem 1.5rem;
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
    padding: 1rem;
    border-bottom: 1px solid #eee;
  }

  .task-list li:last-child {
    border-bottom: none;
  }

  .task-list input[type="checkbox"] {
    cursor: pointer;
    width: 20px;
    height: 20px;
  }

  .task-list span {
    flex: 1;
    word-break: break-word;
    font-size: 1rem;
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
    font-size: 1.5rem;
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
