const { createApp, ref, computed, nextTick, watch, onMounted } = Vue;

createApp({
  setup(){
    const stage = ref('landing');
    const landingSection = ref('');
    const appShell = ref('workspace');
    const roleView = ref('manager');
    const currentView = ref('dashboard');
    const currentProjectId = ref('q3');
    const toastMsg = ref('');
    const chatInput = ref('');
    const chatLog = ref([]);
    const docInput = ref('');
    const docSummary = ref('');
    const loginEmail = ref('');
    const loginPassword = ref('');
    const loginRole = ref('manager');
    const signupName = ref('');
    const signupEmail = ref('');
    const signupOrg = ref('');
    const signupPassword = ref('');

    const user = { name: 'Alex', initials: 'A' };
    const boardColumns = ['Backlog','In progress','Review','Done'];

    const tenants = [
      { name:'IBM', plan:'Enterprise', status:'Active' },
      { name:'Infosys', plan:'Enterprise', status:'Active' }
    ];
    const templates = [
      { name:'Consulting engagement', desc:'Default roles: PM, BA — checklist: kickoff, weekly sync, status report' },
      { name:'Audit engagement', desc:'Default roles: Lead, Reviewer — checklist: evidence request, working papers' }
    ];
    const teamMembers = [
      { name:'Anjali Gupta', role:'Consultant', active:3 },
      { name:'Tarang Jhaveri', role:'Analyst', active:2 }
    ];

    const projects = ref([
      { id:'q3', name:'Q3 Onboarding', client:'Acme Co', members:6, jiraKey:'ACME-Q3' },
      { id:'audit26', name:'Audit 2026', client:'Beta Corp', members:4, jiraKey:'BETA-AU26' }
    ]);

    const tasksByProject = {
      q3: [
        { id:1, title:'Reconcile working papers', owner:'TJ', due:'Sep 22', status:'Backlog', risk:true, ai:true, source:'Finance sync, Sep 19', start:4, end:8 },
        { id:2, title:'Draft engagement letter', owner:'AG', due:'Sep 24', status:'In progress', risk:false, ai:false, source:'MSA_v3.pdf', start:1, end:10 },
        { id:3, title:'Update client tracker', owner:'AI', due:'Sep 20', status:'Review', risk:false, ai:true, source:'Kickoff call, Sep 15', start:2, end:6 },
        { id:4, title:'Kickoff call held', owner:'AG', due:'Sep 15', status:'Done', risk:false, ai:false, source:'Calendar', start:0, end:1 }
      ],
      audit26: [
        { id:5, title:'Evidence request — vendor list', owner:'TJ', due:'Sep 26', status:'Backlog', risk:false, ai:true, source:'Client email, Sep 18', start:5, end:12 },
        { id:6, title:'Review working papers', owner:'AG', due:'Sep 23', status:'In progress', risk:true, ai:false, source:'Manual', start:3, end:9 }
      ]
    };
    const meetingsByProject = {
      q3: [ { title:'Client sync', time:'Tomorrow, 3:00 PM' }, { title:'Internal review', time:'Fri, 11:00 AM' } ],
      audit26: [ { title:'Evidence walkthrough', time:'Thu, 2:00 PM' } ]
    };
    const momsByProject = {
      q3: [
        { title:'Client sync — Sep 18', summary:'3 action items, 1 risk flagged', actions:['Reconcile working papers','Send draft','Confirm scope'] },
        { title:'Kickoff call — Sep 15', summary:'5 action items', actions:['Share timeline','Assign leads','Set up tracker'] }
      ],
      audit26: [
        { title:'Planning call — Sep 14', summary:'2 action items', actions:['Request evidence','Schedule walkthrough'] }
      ]
    };
    const jiraByProject = {
      q3: { open:12, sprint:8, overdue:2, progress:62 },
      audit26: { open:5, sprint:5, overdue:0, progress:40 }
    };
    const weeklyByProject = {
      q3: { weekly:[0,1,0,1,1,0,1], daily:[0,1,0,1,1,0,1] },
      audit26: { weekly:[0,0,1,0,0,1,0], daily:[0,0,1,0,0,1,0] }
    };
    const dayLabels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

    const currentProject = computed(() => projects.value.find(p => p.id === currentProjectId.value));
    const currentTasks = computed(() => tasksByProject[currentProjectId.value] || []);
    const visibleTasks = computed(() => roleView.value === 'manager' ? currentTasks.value : currentTasks.value.filter(t => t.owner !== 'AI'));
    const currentMeetings = computed(() => meetingsByProject[currentProjectId.value] || []);
    const currentMoms = computed(() => momsByProject[currentProjectId.value] || []);
    const currentJira = computed(() => jiraByProject[currentProjectId.value] || { open:0, sprint:0, overdue:0, progress:0 });
    const currentRiskCount = computed(() => visibleTasks.value.filter(t => t.risk).length);
    const focusTask = computed(() => { const t = visibleTasks.value.find(x => x.status !== 'Done'); return t ? t.title : 'All caught up'; });
    const pageTitleMap = { dashboard:'Project Dashboard', board:'', mom:'Minutes of Meeting', documents:'Documents', reports:'Reports', jira:'Jira Metrics', team:'Team', chat:'Chat' };
    const pageTitle = computed(() => currentView.value === 'board' ? (roleView.value==='manager' ? 'Deliverables' : 'My Tasks') : (pageTitleMap[currentView.value] || 'Dashboard'));

    const timelineDays = 17;
    const ganttRows = computed(() => visibleTasks.value.map(t => ({
      ...t,
      leftPct: (t.start / timelineDays) * 100,
      widthPct: Math.max(((t.end - t.start + 1) / timelineDays) * 100, 6)
    })));

    const statusColors = { 'Backlog':'#8B5CF6', 'In progress':'#4C6FFF', 'Review':'#F59E0B', 'Done':'#10B981' };
    const statusBreakdown = computed(() => boardColumns.map(col => ({
      status: col,
      count: visibleTasks.value.filter(t => t.status === col).length,
      color: statusColors[col]
    })).filter(s => s.count > 0 || true));

    const topInsights = computed(() => {
      const items = [];
      if(currentRiskCount.value > 0){
        const risky = visibleTasks.value.find(t => t.risk);
        items.push({ icon:'warning', bg:'var(--red-soft)', color:'var(--red)', title:'Deadline risk detected', sub: risky ? risky.title + ' may slip' : 'A task may slip', time:'1h ago' });
      } else {
        items.push({ icon:'check_circle', bg:'var(--green-soft)', color:'var(--green)', title:'Nothing at risk', sub:'All tasks tracking on time', time:'1h ago' });
      }
      if(currentMeetings.value.length){
        items.push({ icon:'event', bg:'var(--amber-soft)', color:'var(--amber)', title:'Upcoming meeting', sub: currentMeetings.value[0].title + ', ' + currentMeetings.value[0].time, time:'3h ago' });
      }
      const aiTask = visibleTasks.value.find(t => t.ai);
      if(aiTask){
        items.push({ icon:'smart_toy', bg:'var(--blue-soft)', color:'var(--blue)', title:'New task found', sub: aiTask.title + ' — ' + aiTask.source, time:'5h ago' });
      }
      if(roleView.value === 'manager' && currentJira.value.overdue === 0){
        items.push({ icon:'link', bg:'var(--purple-soft)', color:'var(--purple)', title:'Jira sprint on track', sub:'No overdue tickets right now', time:'6h ago' });
      }
      return items;
    });

    const ticketColors = ['#4C6FFF','#10B981','#F59E0B','#8B5CF6','#EF4444'];
    const ticketItems = computed(() => {
      return visibleTasks.value.filter(t => t.ai || t.risk).slice(0,4).map((t,i) => ({
        title: t.title,
        initials: t.owner.slice(0,2).toUpperCase(),
        color: ticketColors[i % ticketColors.length],
        msg: t.ai ? ('Found from ' + t.source + ' — review and confirm.') : (t.owner + ' may slip on this — worth a check-in.')
      }));
    });

    const chartPeriod = ref('weekly');
    const mainChartRef = ref(null);
    const donutChartRef = ref(null);
    let chartInstances = {};

    function destroyChart(key){
      if(chartInstances[key]){ chartInstances[key].destroy(); delete chartInstances[key]; }
    }
    function renderDashboardCharts(){
      if(stage.value !== 'app' || appShell.value !== 'workspace' || currentView.value !== 'dashboard') return;
      nextTick(() => {
        if(mainChartRef.value){
          destroyChart('main');
          const wk = weeklyByProject[currentProjectId.value] || weeklyByProject.q3;
          const data = chartPeriod.value === 'weekly' ? wk.weekly : wk.daily;
          chartInstances.main = new Chart(mainChartRef.value.getContext('2d'), {
            type:'line',
            data:{ labels:dayLabels, datasets:[{ label:'Tasks completed', data, borderColor:'#2F6FED', backgroundColor:'rgba(47,111,237,0.12)', fill:true, tension:0.4, pointRadius:3, pointBackgroundColor:'#2F6FED', borderWidth:2.5 }] },
            options:{ responsive:true, maintainAspectRatio:false,
              plugins:{ legend:{display:false} },
              scales:{ y:{ beginAtZero:true, grid:{color:'#ECEDF2'}, ticks:{font:{size:10.5},stepSize:1} }, x:{ grid:{display:false}, ticks:{font:{size:10.5}} } } }
          });
        }
        if(donutChartRef.value){
          destroyChart('donut');
          const breakdown = statusBreakdown.value.filter(s => s.count > 0);
          chartInstances.donut = new Chart(donutChartRef.value.getContext('2d'), {
            type:'doughnut',
            data:{ labels:breakdown.map(s=>s.status), datasets:[{ data:breakdown.map(s=>s.count), backgroundColor:breakdown.map(s=>s.color), borderWidth:0 }] },
            options:{ responsive:true, maintainAspectRatio:false, cutout:'72%', plugins:{ legend:{display:false}, tooltip:{enabled:true} } }
          });
        }
      });
    }

    onMounted(() => { renderDashboardCharts(); });
    watch([stage, currentView, currentProjectId, roleView, chartPeriod], renderDashboardCharts);

    function toast(msg){
      toastMsg.value = msg;
      setTimeout(() => { toastMsg.value = ''; }, 2600);
    }
    function toggleLanding(section){
      landingSection.value = landingSection.value === section ? '' : section;
    }
    function doLogin(){
      if(loginRole.value === 'super_admin'){
        appShell.value = 'super_admin';
      } else if(loginRole.value === 'tenant_admin'){
        appShell.value = 'tenant_admin';
      } else {
        appShell.value = 'workspace';
        roleView.value = loginRole.value;
        currentView.value = 'dashboard';
      }
      stage.value = 'app';
    }
    function logout(){
      stage.value = 'landing';
      chatLog.value = [];
      docSummary.value = '';
    }
    function sendChat(){
      const q = chatInput.value.trim();
      if(!q) return;
      chatLog.value.push({ role:'user', text:q });
      let answer = "I couldn't find anything specific on that yet — try asking about deadlines, risk, or a named task.";
      const lower = q.toLowerCase();
      if(lower.includes('block') || lower.includes('risk') || lower.includes('behind')){
        const risky = visibleTasks.value.find(t => t.risk);
        answer = risky ? `${risky.title} is flagged at risk, owned by ${risky.owner}. Source: ${risky.source}` : 'Nothing is currently flagged at risk on this project.';
      } else if(lower.includes('meeting')){
        answer = currentMeetings.value.length ? `Next up: ${currentMeetings.value[0].title}, ${currentMeetings.value[0].time}.` : 'No upcoming meetings on the calendar.';
      } else if(lower.includes('status') || lower.includes('progress')){
        const done = visibleTasks.value.filter(t=>t.status==='Done').length;
        answer = `${done} of ${visibleTasks.value.length} tasks are done on ${currentProject.value.name}.`;
      } else if(lower.includes('jira')){
        answer = `${currentJira.value.open} open tickets, ${currentJira.value.overdue} overdue, sprint at ${currentJira.value.progress}% on ${currentProject.value.jiraKey}.`;
      }
      chatLog.value.push({ role:'bot', text:answer });
      chatInput.value = '';
    }
    function summarizeDoc(){
      if(!docInput.value.trim()){
        docSummary.value = 'Paste some text first.';
        return;
      }
      docSummary.value = 'Contract covers scope, a 90-day term, and a deliverable clause referenced in current tasks. (This is a placeholder — real summarisation happens once the RAG backend is connected.)';
    }

    return {
      stage, landingSection, toggleLanding, appShell, roleView, currentView, currentProjectId, user, boardColumns,
      tenants, templates, teamMembers, projects, currentProject,
      currentTasks, visibleTasks, currentMeetings, currentMoms, currentJira,
      currentRiskCount, focusTask, pageTitle, toastMsg, toast, ganttRows,
      loginEmail, loginPassword, loginRole, signupName, signupEmail, signupOrg, signupPassword, doLogin, logout,
      chatInput, chatLog, sendChat, docInput, docSummary, summarizeDoc,
      statusBreakdown, topInsights, ticketItems, chartPeriod,
      mainChartRef, donutChartRef
    };
  }
}).mount('#app');