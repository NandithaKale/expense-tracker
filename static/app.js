var _origFetch = window.fetch;
window.fetch = function(url, opts) {
  opts = opts || {};
  opts.credentials = "include";
  return _origFetch(url, opts);
};

var CATS = {
  Food:          { icon: "🍔", color: "#f39c12" },
  Transport:     { icon: "🚗", color: "#3498db" },
  Shopping:      { icon: "🛍️", color: "#9b59b6" },
  Bills:         { icon: "💡", color: "#e74c3c" },
  Health:        { icon: "🏥", color: "#2ecc71" },
  Entertainment: { icon: "🎬", color: "#e67e22" },
  Other:         { icon: "📦", color: "#95a5a6" }
};
var INC_CATS = { Salary:"💼", Freelance:"💻", Business:"🏢", Investment:"📈", Rental:"🏠", Other:"📦" };

var me                 = null;
var allUsers           = [];
var allExpenses        = [];
var allIncome          = [];
var activeFilter       = "All";
var activeMemberFilter = null;
var catChart           = null;
var monthChart         = null;
var familyChart        = null;
var budget             = 0;

function fmt(n) { return "₹" + Number(n).toLocaleString("en-IN"); }

function showToast(msg, type) {
  var t = document.getElementById("toast");
  if (!t) return;
  t.textContent = msg;
  t.style.borderColor = type === "error" ? "#ff6b6b" : type === "success" ? "#3dd68c" : "#353545";
  t.classList.add("show");
  setTimeout(function() { t.classList.remove("show"); }, 2500);
}

function avatar(name) {
  if (!name) return "?";
  return name.split(" ").map(function(w) { return w[0]; }).join("").slice(0, 2).toUpperCase();
}

function showSection(id, el) {
  document.querySelectorAll(".section").forEach(function(s) { s.classList.remove("active"); });
  document.querySelectorAll(".nav-item").forEach(function(n) { n.classList.remove("active"); });
  document.getElementById("sec-" + id).classList.add("active");
  el.classList.add("active");
  if (id === "family")   renderFamilySection();
  if (id === "expenses") { renderExpenseFilters(); renderExpenseList(); }
  if (id === "income")   renderIncomeList();
}

// ── Auth ──────────────────────────────────────────────────────

async function loadMe() {
  try {
    var res = await fetch("/api/auth/me");
    if (!res.ok) { window.location.href = "/login"; return; }
    me         = await res.json();
    me.user_id  = parseInt(me.user_id);
    me.family_id = parseInt(me.family_id);

    document.getElementById("userName").textContent      = me.display_name;
    document.getElementById("userRole").textContent      = me.role;
    document.getElementById("userAvatar").textContent    = avatar(me.display_name);
    document.getElementById("familyNameLabel").textContent = me.family_name || "FamilyTrack";
  } catch (err) {
    window.location.href = "/login";
  }
}

async function logout() {
  await fetch("/api/auth/logout", { method: "POST" });
  window.location.href = "/login";
}

// ── Users ─────────────────────────────────────────────────────

async function loadUsers() {
  try {
    var res  = await fetch("/api/users");
    var data = await res.json();
    allUsers  = data.map(function(u) { u.id = parseInt(u.id); return u; });
    renderMembersList();
  } catch (err) { console.error("loadUsers:", err); }
}

function renderMembersList() {
  var wrap = document.getElementById("membersList");
  if (!wrap) return;
  wrap.innerHTML = allUsers.map(function(u) {
    return '<div class="member-chip">' +
      '<div class="avatar">' + avatar(u.display_name) + '</div>' +
      '<div><div class="m-name">' + u.display_name + '</div>' +
      '<div class="m-role">' + u.role + '</div></div></div>';
  }).join("");
}

// ── Budget ────────────────────────────────────────────────────

async function loadBudget() {
  try {
    var res  = await fetch("/api/budget");
    var data = await res.json();
    budget   = parseFloat(data.budget) || 0;
  } catch (err) { console.error("loadBudget:", err); }
}

async function setBudget() {
  var val = parseFloat(document.getElementById("budgetInputMain").value);
  if (isNaN(val) || val <= 0) { showToast("Enter a valid amount", "error"); return; }
  try {
    await fetch("/api/budget", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({amount: val}) });
    showToast("Budget updated!", "success");
    await loadBudget();
    renderOverview();
  } catch (err) { showToast("Failed to set budget", "error"); }
}

// ── Expenses ──────────────────────────────────────────────────

async function loadExpenses() {
  try {
    var res     = await fetch("/api/expenses");
    var data    = await res.json();
    allExpenses = data.map(function(e) { e.user_id = parseInt(e.user_id); e.amount = parseFloat(e.amount); return e; });
  } catch (err) { console.error("loadExpenses:", err); }
}

async function addExpense() {
  var nameEl   = document.getElementById("expName");
  var amountEl = document.getElementById("expAmount");
  var catEl    = document.getElementById("expCategory");
  var typeEl   = document.getElementById("expType");
  var dateEl   = document.getElementById("expDate");
  var tagEl    = document.getElementById("expTag");

  var name   = nameEl.value.trim();
  var amount = amountEl.value.trim();
  var cat    = catEl.value;
  var type   = typeEl.value;
  var date   = dateEl.value;
  var tag    = tagEl ? tagEl.value.trim() : "";

  if (!name)   { showToast("Enter a description", "error"); return; }
  if (!amount) { showToast("Enter an amount",     "error"); return; }
  if (!date)   { showToast("Select a date",       "error"); return; }

  var parsed = parseFloat(amount);
  if (isNaN(parsed) || parsed <= 0) { showToast("Enter a valid amount", "error"); return; }

  try {
    var res  = await fetch("/api/expenses", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({name:name, amount:parsed, category:cat, expense_type:type, tag:tag, date:date}) });
    var data = await res.json();
    if (res.ok) {
      nameEl.value = ""; amountEl.value = ""; if (tagEl) tagEl.value = "";
      showToast("Expense added!", "success");
      await loadExpenses(); renderOverview(); renderExpenseList();
    } else { showToast(data.error || "Failed", "error"); }
  } catch (err) { showToast("Network error", "error"); }
}

async function deleteExpense(id) {
  try {
    await fetch("/api/expenses/" + id, { method: "DELETE" });
    showToast("Deleted", "success");
    await loadExpenses(); renderOverview(); renderExpenseList();
  } catch (err) { console.error(err); }
}

// ── Income ────────────────────────────────────────────────────

async function loadIncome() {
  try {
    var res   = await fetch("/api/income");
    var data  = await res.json();
    allIncome = data.map(function(i) { i.user_id = parseInt(i.user_id); i.amount = parseFloat(i.amount); return i; });
  } catch (err) { console.error("loadIncome:", err); }
}

async function addIncome() {
  var amountEl   = document.getElementById("incAmount");
  var categoryEl = document.getElementById("incCategory");
  var monthEl    = document.getElementById("incMonth");
  var noteEl     = document.getElementById("incNote");

  var amount   = amountEl.value.trim();
  var category = categoryEl.value;
  var month    = monthEl.value;
  var note     = noteEl ? noteEl.value.trim() : "";

  if (!amount) { showToast("Enter an amount", "error"); return; }
  if (!month)  { showToast("Select a month",  "error"); return; }

  var parsed = parseFloat(amount);
  if (isNaN(parsed) || parsed <= 0) { showToast("Enter a valid amount", "error"); return; }

  try {
    var res  = await fetch("/api/income", { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({amount:parsed, category:category, month:month, note:note}) });
    var data = await res.json();
    if (res.ok) {
      amountEl.value = ""; if (noteEl) noteEl.value = "";
      showToast("Income added!", "success");
      await loadIncome(); renderOverview(); renderIncomeList();
    } else { showToast(data.error || "Failed", "error"); }
  } catch (err) { showToast("Network error", "error"); }
}

async function deleteIncome(id) {
  try {
    await fetch("/api/income/" + id, { method: "DELETE" });
    showToast("Deleted", "success");
    await loadIncome(); renderOverview(); renderIncomeList();
  } catch (err) { console.error(err); }
}

// ── Overview ──────────────────────────────────────────────────

function renderOverview() {
  if (!me) return;
  var now   = new Date();
  var month = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0");
  var el    = document.getElementById("overviewMonth");
  if (el) el.textContent = now.toLocaleDateString("en-IN", { month:"long", year:"numeric" });

  var myExp   = allExpenses.filter(function(e) { return e.user_id === me.user_id; });
  var myTotal = myExp.reduce(function(s,e) { return s + e.amount; }, 0);

  var e1 = document.getElementById("myTotalSpent"); if(e1) e1.textContent = fmt(myTotal);
  var e2 = document.getElementById("myTxnCount");   if(e2) e2.textContent = myExp.length + " transactions";

  var myInc      = allIncome.filter(function(i) { return i.user_id === me.user_id && i.month === month; });
  var myIncTotal = myInc.reduce(function(s,i) { return s + i.amount; }, 0);
  var myNet      = myIncTotal - myTotal;
  var e3 = document.getElementById("myTotalIncome"); if(e3) e3.textContent = fmt(myIncTotal);
  var e4 = document.getElementById("myNet"); if(e4) { e4.textContent = "Net " + fmt(myNet); e4.style.color = myNet >= 0 ? "var(--green)" : "var(--red)"; }

  var famTotal = allExpenses.reduce(function(s,e) { return s + e.amount; }, 0);
  var famInc   = allIncome.filter(function(i) { return i.month === month; }).reduce(function(s,i) { return s + i.amount; }, 0);
  var famNet   = famInc - famTotal;

  var e5 = document.getElementById("familyTotalSpent");  if(e5) e5.textContent = fmt(famTotal);
  var e6 = document.getElementById("familyMemCount");    if(e6) e6.textContent = allUsers.length + " members";
  var e7 = document.getElementById("familyTotalIncome"); if(e7) e7.textContent = fmt(famInc);
  var e8 = document.getElementById("familyNet"); if(e8) { e8.textContent = "Net " + fmt(famNet); e8.style.color = famNet >= 0 ? "var(--green)" : "var(--red)"; }

  var pct = budget > 0 ? Math.min((myTotal / budget) * 100, 100) : 0;
  var bar = document.getElementById("barFill"); var pEl = document.getElementById("budgetPct");
  if(bar) { bar.style.width = pct + "%"; bar.className = "bar-fill" + (pct >= 100 ? " over" : pct >= 75 ? " warn" : ""); }
  if(pEl) pEl.textContent = Math.round(pct) + "%";
  var sl = document.getElementById("spentLabel");  if(sl) sl.textContent = fmt(myTotal) + " spent";
  var bl = document.getElementById("budgetLabel"); if(bl) bl.textContent = "Budget: " + fmt(budget);

  renderCharts();
}

function renderCharts() {
  if (!me) return;
  var myExp     = allExpenses.filter(function(e) { return e.user_id === me.user_id; });
  var catTotals = {};
  myExp.forEach(function(e) { catTotals[e.category] = (catTotals[e.category] || 0) + e.amount; });
  var catLabels = Object.keys(catTotals);
  var catValues = Object.values(catTotals);
  var catColors = catLabels.map(function(l) { return CATS[l] ? CATS[l].color : "#888"; });

  var cc = document.getElementById("catChart");
  if (cc && catLabels.length > 0) {
    if (catChart) catChart.destroy();
    catChart = new Chart(cc.getContext("2d"), {
      type: "doughnut",
      data: { labels: catLabels, datasets: [{ data: catValues, backgroundColor: catColors, borderWidth: 0 }] },
      options: { responsive:true, maintainAspectRatio:false, plugins: { legend: { position:"bottom", labels:{color:"#888",font:{size:11},padding:10} }, tooltip: { callbacks: { label: function(ctx) { return " " + fmt(ctx.raw); } } } } }
    });
  }

  var monthMap = {};
  myExp.forEach(function(e) { var m = e.date.slice(0,7); monthMap[m] = (monthMap[m]||0) + e.amount; });
  var monthKeys   = Object.keys(monthMap).sort().slice(-6);
  var monthValues = monthKeys.map(function(m) { return monthMap[m]; });

  var mc = document.getElementById("monthChart");
  if (mc && monthKeys.length > 0) {
    if (monthChart) monthChart.destroy();
    monthChart = new Chart(mc.getContext("2d"), {
      type: "bar",
      data: { labels: monthKeys, datasets: [{ label:"Spent", data:monthValues, backgroundColor:"#6c63ff", borderRadius:6, borderSkipped:false }] },
      options: { responsive:true, maintainAspectRatio:false, plugins: { legend:{display:false}, tooltip:{callbacks:{label:function(ctx){return " "+fmt(ctx.raw);}}} }, scales: { y:{beginAtZero:true,ticks:{callback:function(v){return "₹"+v.toLocaleString("en-IN");},color:"#888",font:{size:11}},grid:{color:"#2a2a35"}}, x:{grid:{display:false},ticks:{color:"#888",font:{size:11}}} } }
    });
  }
}

// ── Expense List ──────────────────────────────────────────────

function renderExpenseFilters() {
  var usedCats = [];
  allExpenses.forEach(function(e) { if (usedCats.indexOf(e.category) === -1) usedCats.push(e.category); });
  var chips = document.getElementById("filterChips");
  if (chips) {
    chips.innerHTML = ["All"].concat(usedCats).map(function(cat) {
      var label  = cat === "All" ? "All" : ((CATS[cat] ? CATS[cat].icon : "") + " " + cat);
      var active = cat === activeFilter ? " active" : "";
      return '<button class="chip' + active + '" onclick="setFilter(\'' + cat + '\', this)">' + label + '</button>';
    }).join("");
  }
  var mf = document.getElementById("memberFilter");
  if (mf) {
    mf.innerHTML = allUsers.map(function(u) {
      var active = activeMemberFilter === u.id ? " active" : "";
      return '<button class="chip' + active + '" onclick="setMemberFilter(' + u.id + ', this)">' + avatar(u.display_name) + " " + u.display_name + '</button>';
    }).join("");
  }
}

function setFilter(cat, el) {
  activeFilter = cat;
  document.querySelectorAll("#filterChips .chip").forEach(function(c) { c.classList.remove("active"); });
  el.classList.add("active");
  renderExpenseList();
}

function setMemberFilter(uid, el) {
  activeMemberFilter = activeMemberFilter === uid ? null : uid;
  document.querySelectorAll("#memberFilter .chip").forEach(function(c) { c.classList.remove("active"); });
  if (activeMemberFilter) el.classList.add("active");
  renderExpenseList();
}

function renderExpenseList() {
  renderExpenseFilters();
  var data = allExpenses
    .filter(function(e) { return activeFilter === "All" || e.category === activeFilter; })
    .filter(function(e) { return !activeMemberFilter || e.user_id === activeMemberFilter; })
    .sort(function(a,b) { return new Date(b.date) - new Date(a.date); });

  var list = document.getElementById("expenseList");
  if (!list) return;
  if (!data.length) { list.innerHTML = '<div class="empty">No expenses found. Add one above!</div>'; return; }

  list.innerHTML = data.map(function(e) {
    var c    = CATS[e.category] || CATS["Other"];
    var user = null; for (var i=0;i<allUsers.length;i++) { if(allUsers[i].id===e.user_id){user=allUsers[i];break;} }
    var meta = [new Date(e.date).toLocaleDateString("en-IN",{day:"numeric",month:"short"}), e.tag?"#"+e.tag:"", user?user.display_name:""].filter(Boolean).join(" · ");
    var canDel = me && (me.role === "admin" || e.user_id === me.user_id);
    var delBtn = canDel ? '<button class="exp-delete" onclick="deleteExpense('+e.id+')">✕</button>' : "";
    return '<div class="expense-item">' +
      '<div class="exp-icon" style="background:'+c.color+'22">'+c.icon+'</div>' +
      '<div class="exp-info"><div class="exp-name">'+e.name+'</div><div class="exp-meta">'+meta+'</div></div>' +
      '<div class="exp-right"><span class="exp-badge">'+e.expense_type+'</span><div class="exp-amount">'+fmt(e.amount)+'</div>'+delBtn+'</div>' +
    '</div>';
  }).join("");
}

// ── Income List ───────────────────────────────────────────────

function renderIncomeList() {
  var data = allIncome.slice().sort(function(a,b) { return b.month.localeCompare(a.month); });
  var list = document.getElementById("incomeList");
  if (!list) return;
  if (!data.length) { list.innerHTML = '<div class="empty">No income added yet.</div>'; return; }
  list.innerHTML = data.map(function(i) {
    var icon   = INC_CATS[i.category] || "📦";
    var user   = null; for (var x=0;x<allUsers.length;x++) { if(allUsers[x].id===i.user_id){user=allUsers[x];break;} }
    var canDel = me && (me.role === "admin" || i.user_id === me.user_id);
    var meta   = [i.month, i.note, user?user.display_name:""].filter(Boolean).join(" · ");
    var delBtn = canDel ? '<button class="exp-delete" onclick="deleteIncome('+i.id+')">✕</button>' : "";
    return '<div class="expense-item">' +
      '<div class="exp-icon" style="background:#3dd68c22">'+icon+'</div>' +
      '<div class="exp-info"><div class="exp-name">'+i.category+'</div><div class="exp-meta">'+meta+'</div></div>' +
      '<div class="exp-right"><div class="exp-amount" style="color:var(--green)">'+fmt(i.amount)+'</div>'+delBtn+'</div>' +
    '</div>';
  }).join("");
}

// ── Family Section ────────────────────────────────────────────

async function renderFamilySection() {
  // Show invite code only to admin
  var inviteCard = document.getElementById("inviteCard");
  var inviteCode = document.getElementById("inviteCodeCard");
  if (inviteCard && me) {
    if (me.role === "admin") {
      inviteCard.style.display = "flex";
      if (inviteCode) inviteCode.textContent = me.invite_code || "------";
    } else {
      inviteCard.style.display = "none";
    }
  }

  try {
    var res  = await fetch("/api/summary/family");
    var data = await res.json();
    var cards = document.getElementById("familyCards");
    if (cards) {
      cards.innerHTML = data.map(function(m) {
        var netColor = m.net >= 0 ? "var(--green)" : "var(--red)";
        return '<div class="family-card">' +
          '<div class="fc-avatar">' + avatar(m.display_name) + '</div>' +
          '<div class="fc-name">'   + m.display_name + '</div>' +
          '<div class="fc-row"><span class="label">Income</span><span class="val" style="color:var(--green)">'   + fmt(m.total_income)   + '</span></div>' +
          '<div class="fc-row"><span class="label">Expenses</span><span class="val" style="color:var(--red)">'  + fmt(m.total_expenses) + '</span></div>' +
          '<div class="fc-net"><span>Net</span><span style="color:'+netColor+'">' + fmt(m.net) + '</span></div>' +
        '</div>';
      }).join("");
    }

    var fc = document.getElementById("familyChart");
    if (fc && data.length > 0) {
      if (familyChart) familyChart.destroy();
      familyChart = new Chart(fc.getContext("2d"), {
        type: "bar",
        data: {
          labels: data.map(function(m) { return m.display_name; }),
          datasets: [
            { label:"Income",   data:data.map(function(m){return m.total_income;}),   backgroundColor:"#3dd68c", borderRadius:6, borderSkipped:false },
            { label:"Expenses", data:data.map(function(m){return m.total_expenses;}), backgroundColor:"#6c63ff", borderRadius:6, borderSkipped:false }
          ]
        },
        options: { responsive:true, maintainAspectRatio:false, plugins:{legend:{labels:{color:"#888",font:{size:12},padding:16}},tooltip:{callbacks:{label:function(ctx){return " "+fmt(ctx.raw);}}}}, scales:{y:{beginAtZero:true,ticks:{callback:function(v){return "₹"+v.toLocaleString("en-IN");},color:"#888"},grid:{color:"#2a2a35"}},x:{grid:{display:false},ticks:{color:"#888"}}} }
      });
    }
  } catch (err) { console.error("renderFamilySection:", err); }
}

// ── Init ──────────────────────────────────────────────────────

async function init() {
  try {
    await loadMe();
    await Promise.all([loadUsers(), loadBudget(), loadExpenses(), loadIncome()]);
    var expDate = document.getElementById("expDate"); if(expDate) expDate.valueAsDate = new Date();
    var incMonth = document.getElementById("incMonth");
    if (incMonth) { var now = new Date(); incMonth.value = now.getFullYear() + "-" + String(now.getMonth()+1).padStart(2,"0"); }
    renderOverview();
    renderExpenseList();
    renderIncomeList();
  } catch (err) { console.error("init:", err); }
}

init();