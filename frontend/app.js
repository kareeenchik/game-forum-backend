const API_AUTH = 'http://127.0.0.1:8001/api/v1/auth';
const API_FORUM = 'http://127.0.0.1:8002/api/v1/forum';
const API_LOGS = 'http://127.0.0.1:8003/api/v1/logs';

let currentTopicId = null;
let currentTopicAuthorId = null;
let lastCommentsCount = 0;
let notificationInterval = null;
let categoriesCache = {}; 

const log = (m) => {
    const bar = document.getElementById('log-bar');
    if(bar) bar.innerText = `Состояние: ${m}`;
};

function showNotification(text) {
    const toast = document.getElementById('notification-toast');
    const msg = document.getElementById('notification-msg');
    if (!toast || !msg) return;
    msg.innerText = text;
    toast.classList.remove('hidden');
    setTimeout(() => { toast.classList.add('hidden'); }, 4000); 
}

function switchAuth(type) {
    const isLogin = type === 'login';
    document.getElementById('login-form').classList.toggle('hidden', !isLogin);
    document.getElementById('register-form').classList.toggle('hidden', isLogin);
    document.getElementById('tab-login').classList.toggle('active', isLogin);
    document.getElementById('tab-register').classList.toggle('active', !isLogin);
}

async function handleRegister() {
    const username = document.getElementById('reg-user').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-pass').value;
    if (!username || !password || !email) return alert("Заполните все поля!");
    try {
        const res = await fetch(`${API_AUTH}/register/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username, email, nickname: username, password })
        });
        if (res.ok) { alert("Регистрация успешна!"); switchAuth('login'); }
        else { const err = await res.json(); alert("Ошибка: " + JSON.stringify(err)); }
    } catch (e) { log("❌ Ошибка связи с Auth"); }
}

async function handleLogin() {
    const username = document.getElementById('user').value;
    const password = document.getElementById('pass').value;
    if (!username || !password) return alert("Заполните поля!");
    try {
        const res = await fetch(`${API_AUTH}/login/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username, password })
        });
        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('author_id', data.user_id || data.id); 
            localStorage.setItem('user_name', username);
            localStorage.setItem('user_role', data.role || 'user'); 
            
            document.getElementById('auth-page').classList.add('hidden');
            document.getElementById('main-page').classList.remove('hidden');
            initApp(); 
        } else { alert("Неверный логин или пароль!"); }
    } catch (e) { log("❌ Ошибка соединения"); }
}

function handleLogout() {
    if(notificationInterval) clearInterval(notificationInterval);
    localStorage.clear(); 
    window.location.reload(); 
}

async function loadCategories() {
    try {
        const res = await fetch(`${API_FORUM}/categories/`);
        const data = await res.json();
        const cats = Array.isArray(data) ? data : (data.results || []);
        
        const createSelect = document.getElementById('topic-category-select');
        const filterSelect = document.getElementById('filter-category');

        categoriesCache = {};
        let options = '';
        cats.forEach(c => {
            categoriesCache[c.id] = c.name;
            options += `<option value="${c.id}">${c.name}</option>`;
        });

        if (createSelect) createSelect.innerHTML = '<option value="">Выберите категорию...</option>' + options;
        if (filterSelect) filterSelect.innerHTML = '<option value="">Все категории</option>' + options;
    } catch (e) { log("❌ Ошибка категорий"); }
}

async function loadTopics() {
    try {
        if (Object.keys(categoriesCache).length === 0) await loadCategories();
        const res = await fetch(`${API_FORUM}/topics/`);
        const data = await res.json();
        const topics = Array.isArray(data) ? data : (data.results || []);
        
        const filterId = document.getElementById('filter-category').value;
        const myId = localStorage.getItem('author_id');
        const myRole = localStorage.getItem('user_role');

        const filteredData = filterId 
            ? topics.filter(t => String(t.category) === String(filterId)) 
            : topics;

        const list = document.getElementById('topics-list');
        list.innerHTML = filteredData.map(t => {
            const canDelete = (myRole === 'admin') || (String(t.author_id) === String(myId));
            const catName = categoriesCache[t.category] || "Общее";

            return `
                <div class="topic-item">
                    <div onclick="openTopic(${t.id}, '${t.title}', ${t.author_id}, '${t.content}', '${t.author_name}')" style="cursor:pointer; flex:1;">
                        <strong style="color:var(--green); font-size:1.1em;">${t.title}</strong>
                        <br><small style="color:#888;">Автор: <b style="color:#bbb;">${t.author_name || 'Аноним'}</b> | Раздел: ${catName}</small>
                    </div>
                    ${canDelete ? `<button onclick="handleDeleteTopic(${t.id})" style="background:var(--red); color:white; padding:5px 10px; border-radius:4px; cursor:pointer; border:none;">Удалить</button>` : ''}
                </div>
            `;
        }).join('') || "Тем пока нет";
    } catch (e) { log("❌ Ошибка ленты"); }
}

async function handleCreateTopic() {
    const title = document.getElementById('topic-title').value;
    const content = document.getElementById('topic-content').value;
    const categoryId = document.getElementById('topic-category-select').value;
    if (!title || !content || !categoryId) return alert("Заполните все поля!");

    try {
        const res = await fetch(`${API_FORUM}/topics/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                title, content, category: categoryId,
                author_id: parseInt(localStorage.getItem('author_id')),
                author_name: localStorage.getItem('user_name') 
            })
        });
        if (res.ok) {
            document.getElementById('topic-title').value = '';
            document.getElementById('topic-content').value = '';
            loadTopics();
            log("✅ Тема создана!");
        }
    } catch (e) { log("❌ Ошибка создания"); }
}

async function handleDeleteTopic(topicId) {
    if (!confirm("Удалить тему?")) return;
    try {
        const res = await fetch(`${API_FORUM}/topics/${topicId}/`, {
            method: 'DELETE',
            headers: {
                'X-User-Id': localStorage.getItem('author_id'),
                'X-User-Role': localStorage.getItem('user_role')
            }
        });
        if (res.ok) { loadTopics(); log("🗑️ Тема удалена"); }
    } catch (e) { log("❌ Ошибка удаления"); }
}


async function openTopic(id, title, authorId, content, authorName) {
    currentTopicId = id;
    currentTopicAuthorId = authorId;
    document.getElementById('main-page').classList.add('hidden');
    document.getElementById('topic-detail').classList.remove('hidden');
    document.getElementById('current-topic-title').innerText = title;
    
    const contentBox = document.getElementById('current-topic-content');
    contentBox.innerHTML = `<div class="author-badge"><span style="color:#888">Автор:</span> <b style="color:var(--green)">${authorName || 'Аноним'}</b></div><div class="topic-text">${content}</div>`;
    
    window.scrollTo(0, 0);
    lastCommentsCount = 0;
    await refreshComments(true); 
    if(notificationInterval) clearInterval(notificationInterval);
    notificationInterval = setInterval(() => refreshComments(false), 5000);
}

async function refreshComments(isFirstLoad = false) {
    try {
        const res = await fetch(`${API_FORUM}/posts/`);
        const data = await res.json();
        const allPosts = Array.isArray(data) ? data : (data.results || []);
        const filtered = allPosts.filter(p => Number(p.topic) === Number(currentTopicId));

        const myId = localStorage.getItem('author_id');
        const myRole = localStorage.getItem('user_role');

        if (!isFirstLoad && filtered.length > lastCommentsCount) {
            const lastPost = filtered[filtered.length - 1];
            if (String(currentTopicAuthorId) === String(myId) && String(lastPost.author_id) !== String(myId)) {
                showNotification(`Новый ответ от ${lastPost.author_name}!`);
            }
        }
        lastCommentsCount = filtered.length;

        const list = document.getElementById('comments-list');
        list.innerHTML = filtered.map(p => {
            const canDelete = (myRole === 'admin') || 
                              (String(p.author_id) === String(myId)) || 
                              (String(currentTopicAuthorId) === String(myId));

            return `
                <div style="background:#222; padding:12px; margin-bottom:10px; border-radius:6px; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong style="color:var(--green)">${p.author_name || 'Аноним'}</strong>
                        <p style="margin:5px 0; color:#ccc;">${p.content}</p>
                    </div>
                    ${canDelete ? `<button onclick="handleDeletePost(${p.id})" style="background:none; color:var(--red); border:1px solid var(--red); cursor:pointer; padding:3px 7px; border-radius:4px;">Удалить</button>` : ''}
                </div>
            `;
        }).join('') || "Комментариев нет";
    } catch (e) { }
}

async function handleSendComment() {
    const text = document.getElementById('comment-text').value;
    if (!text) return alert("Введите текст");

    try {
        const res = await fetch(`${API_FORUM}/posts/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-User-Id': localStorage.getItem('author_id'),
                'X-User-Role': localStorage.getItem('user_role')
            },
            body: JSON.stringify({
                topic: parseInt(currentTopicId),
                content: text,
                author_id: parseInt(localStorage.getItem('author_id')),
                author_name: localStorage.getItem('user_name') 
            })
        });
        if (res.ok) {
            document.getElementById('comment-text').value = '';
            refreshComments(true);
        }
    } catch (e) { console.error(e); }
}

async function handleDeletePost(postId) {
    if (!confirm("Удалить комментарий?")) return;
    try {
        const res = await fetch(`${API_FORUM}/posts/${postId}/`, {
            method: 'DELETE',
            headers: {
                'X-User-Id': localStorage.getItem('author_id'),
                'X-User-Role': localStorage.getItem('user_role')
            }
        });
        if (res.ok) refreshComments(true);
    } catch (e) { }
}

function showMain() {
    if(notificationInterval) clearInterval(notificationInterval);
    document.getElementById('topic-detail').classList.add('hidden');
    document.getElementById('main-page').classList.remove('hidden');
    loadTopics();
}

async function loadAuditLogs() {
    const list = document.getElementById('audit-logs-list');
    try {
        const res = await fetch(`${API_LOGS}/all/`); 
        const logs = await res.json();
        list.innerHTML = logs.map(l => `
            <div class="log-entry">
                <span style="color: #666;">[${l.timestamp}]</span> 
                <span class="log-action">${l.action}</span> 
                <span>${l.details} (User ID: ${l.user_id})</span>
            </div>
        `).join('') || "Логов нет";
    } catch (e) { list.innerHTML = "Ошибка связи с сервисом аудита."; }
}

async function handleCreateCategory() {
    const nameInput = document.getElementById('new-category-name');
    const name = nameInput.value;
    if (!name) return;
    try {
        const res = await fetch(`${API_FORUM}/categories/`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-User-Id': localStorage.getItem('author_id'),
                'X-User-Role': localStorage.getItem('user_role') 
            },
            body: JSON.stringify({ name: name })
        });
        if (res.ok) {
            nameInput.value = '';
            loadCategories();
            log("✅ Категория создана");
        }
    } catch (e) { }
}

function initApp() {
    const role = localStorage.getItem('user_role');
    const adminMonitor = document.getElementById('admin-monitor');
    const adminCatPanel = document.getElementById('admin-category-panel');
    
    if (role === 'admin') {
        if (adminMonitor) adminMonitor.classList.remove('hidden');
        if (adminCatPanel) adminCatPanel.classList.remove('hidden');
    }
    loadCategories();
    loadTopics();
}

window.onload = function() {
    if (localStorage.getItem('author_id')) {
        document.getElementById('auth-page').classList.add('hidden');
        document.getElementById('main-page').classList.remove('hidden');
        initApp();
    }
};