
const API="";
const $=s=>document.querySelector(s);

async function api(path,options={}){
  const r=await fetch(API+path,{headers:{"Content-Type":"application/json"},...options});
  if(!r.ok){
    const e=await r.json().catch(()=>({detail:"Request failed"}));
    throw new Error(e.detail||"Request failed");
  }
  return r.json();
}

document.querySelectorAll(".tab").forEach(btn=>btn.addEventListener("click",()=>{
  document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));
  document.querySelectorAll(".tab-panel").forEach(x=>x.classList.remove("active"));
  btn.classList.add("active");
  $("#"+btn.dataset.tab).classList.add("active");
}));

async function init(){
  try{
    const h=await api("/api/health");
    $("#health").textContent="System online · "+h.mode;
    await Promise.all([loadCandidates(),loadVerification(),loadSubscription(),loadContracts()]);
  }catch(e){
    $("#health").textContent="Backend offline";
  }
}

$("#matchForm").addEventListener("submit",async e=>{
  e.preventDefault();
  const payload={
    role_title:$("#roleTitle").value.trim(),
    location:$("#location").value.trim()||null,
    mandatory_skill:$("#mandatorySkill").value.trim()||null,
    min_experience:Number($("#minExperience").value||0),
    required_verification:$("#verificationLevel").value,strict_role_match:$("#strictRole").value==="true"
  };
  try{
    const d=await api("/api/match",{method:"POST",body:JSON.stringify(payload)});
    if(!d.matches.length){
      $("#matchResults").innerHTML=`<b>No eligible candidates matched all mandatory requirements.</b><div class="explain">${d.fallback}</div>`;
      return;
    }
    $("#matchResults").innerHTML=d.matches.map(m=>`
      <div class="card">
        <div class="card-headline">
          <div>
            <h3>${m.candidate.name}</h3>
            <p>${m.candidate.title} · ${m.candidate.location} · ${m.candidate.years_experience} years</p>
          </div>
          <div class="score">${m.score}%</div>
        </div>
        <div class="tags">${m.fulfilled.map(x=>`<span class="tag">${x}</span>`).join("")}</div>
        <div class="explain"><b>Verified evidence:</b> ${m.verified_evidence.qualifications.join(", ")} · Documents ${m.verified_evidence.documents_verified}<br>${m.explanation}</div>
      </div>`).join("");
  }catch(e){
    $("#matchResults").textContent="Match failed: "+e.message;
  }
});

async function loadCandidates(){
  const data=await api("/api/candidates");
  $("#candidateList").innerHTML=data.map(c=>`
    <div class="card">
      <div class="card-headline">
        <div><h3>${c.name}</h3><p>${c.title} · ${c.location} · ${c.availability}</p></div>
        <span class="pill">${c.verification_level}</span>
      </div>
      <p>${c.verified_documents}/${c.total_documents} documents verified · Visibility: ${c.profile_visibility}</p>
      <div class="tags">${c.skills.map(s=>`<span class="tag">${s}</span>`).join("")}</div>
      <div class="explain">Digital passport token: ${c.passport_token}</div>
    </div>`).join("");
}

async function loadVerification(){
  const data=await api("/api/verification");
  $("#verificationList").innerHTML=data.map(v=>`
    <div class="card">
      <div class="card-headline">
        <div><h3>${v.candidate_name}</h3><p>${v.document}</p></div>
        <span class="pill">${v.status}</span>
      </div>
      <p>Expiry: ${v.expires_on||"Not applicable"}</p>
      <div class="tags">
        <button onclick="updateVerification('${v.id}','approved')">Approve</button>
        <button class="secondary" onclick="updateVerification('${v.id}','additional_info_requested')">Request info</button>
        <button class="secondary" onclick="updateVerification('${v.id}','rejected')">Reject</button>
      </div>
    </div>`).join("");
}

async function updateVerification(id,status){
  await api(`/api/verification/${id}`,{method:"POST",body:JSON.stringify({status})});
  await loadVerification();
}

async function loadSubscription(){
  const s=await api("/api/subscription");
  $("#subscriptionCard").innerHTML=`
    <b>${s.company} · ${s.plan}</b>
    <p>Status: ${s.status} · Billing: ${s.billing}</p>
    <div class="card">
      <p>Company users: ${s.company_users.used}/${s.company_users.limit}</p>
      <p>Candidate contacts: ${s.candidate_contacts.used}/${s.candidate_contacts.limit}</p>
      <div class="explain">${s.provider}</div>
    </div>`;
}

$("#costBtn").addEventListener("click",async()=>{
  const d=await api("/api/costs");
  const c=d.pilot_100_500;
  $("#costResult").classList.remove("hidden");
  $("#costResult").innerHTML=`
    <b>Pilot: 100–500 candidates</b>
    <p>AWS EU hosting/database/storage: ${c.aws_eu_hosting_db_storage}</p>
    <p>AI matching: ${c.ai_matching}</p>
    <p>Email/SMS: ${c.email_sms}</p>
    <p>Monitoring/backups/security: ${c.monitoring_backups_security}</p>
    <p>E-signature: ${c.esignature}</p>
    <p>Stripe: ${c.stripe}</p>
    <div class="explain">Estimated third-party total: ${c.estimated_total_excluding_maintenance}</div>`;
});

$("#contractForm").addEventListener("submit",async e=>{
  e.preventDefault();
  await api("/api/contracts",{method:"POST",body:JSON.stringify({
    company:$("#contractCompany").value.trim(),
    template:$("#contractTemplate").value.trim()
  })});
  await loadContracts();
});

async function loadContracts(){
  const data=await api("/api/contracts");
  $("#contractList").innerHTML=data.map(c=>`
    <div class="card">
      <div class="card-headline">
        <div><h3>${c.company}</h3><p>${c.template}</p></div>
        <span class="pill">${c.status}</span>
      </div>
      <div class="explain">${c.provider} · ${c.updated_at}</div>
    </div>`).join("");
}

init();
