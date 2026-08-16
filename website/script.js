function handleContactForm(form){
  form.addEventListener('submit', function(e){
    e.preventDefault();
    const fm = e.target;
    const name = fm.name.value.trim();
    const email = fm.email.value.trim();
    const msg = fm.message.value.trim();
    clearErrors(fm);
    const errors = [];
    if(!name) errors.push({field:'name', msg:'Name is required'});
    if(!email) errors.push({field:'email', msg:'Email is required'});
    else if(!validateEmail(email)) errors.push({field:'email', msg:'Please enter a valid email'});
    if(!msg) errors.push({field:'message', msg:'Message is required'});
    const phone = fm.phone?.value?.trim();
    if(phone && !/^\d{10}$/.test(phone)) errors.push({field:'phone', msg:'Phone number must be exactly 10 digits'});

    if(errors.length){
      // show inline errors
      errors.forEach(err=>{
        const el = fm[err.field];
        if(el){
          showError(el, err.msg);
        }
      });
      showModal('Please fix the errors','There are validation errors in the form.');
      // focus first error
      const first = fm.querySelector('.input-error');
      if(first) first.focus();
      return;
    }

    // require OTP verification for phone/email if provided
    const missingVerification = [];
    if(fm.phone && fm.phone.value.trim()){
      const d = form._otpData?.phone;
      if(!d || !d.verified) missingVerification.push('phone');
    }
    if(fm.email && fm.email.value.trim()){
      const d = form._otpData?.email;
      if(!d || !d.verified) missingVerification.push('email');
    }
    if(missingVerification.length){
      missingVerification.forEach(field=>{
        const el = fm[field]; if(el) showError(el, 'Please verify this field via OTP');
      });
      showModal('OTP required','Please verify your phone and/or email using the OTP before sending the enquiry.');
      const first = fm.querySelector('.input-error'); if(first) first.focus();
      return;
    }

    const subject = encodeURIComponent('Click2hedge Inquiry from '+name);
    const body = encodeURIComponent('Service: '+(fm.service?.value||'')+'\n\n'+msg+'\n\nContact: '+name+' <'+email+'>');

    // Save enquiry: if BACKEND_URL is set, POST to server; otherwise save locally (demo)
    const payload = {name, email, phone: fm.phone?.value?.trim()||'', message: msg};
    const backend = window.BACKEND_URL || null;
    if(backend){
      fetch(backend.replace(/\/$/, '') + '/api/submit_enquiry', {
        method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify(payload)
      }).then(r=>r.json()).then(j=>{
        if(j.ok){ showModal('Inquiry saved','Your inquiry was saved (id: '+j.id+'). Your mail client will open next.'); }
        else showModal('Save failed','Could not save enquiry: '+(j.message||'unknown'));
        setTimeout(()=>{ window.location.href = 'mailto:hello@click2hedge.example?subject='+subject+'&body='+body; },800);
      }).catch(err=>{ console.error(err); showModal('Network error','Could not save enquiry to server.'); setTimeout(()=>{ window.location.href = 'mailto:hello@click2hedge.example?subject='+subject+'&body='+body; },800); });
    } else {
      // Demo: save to localStorage
      try{
        const key = 'click2hedge_enquiries';
        const arr = JSON.parse(localStorage.getItem(key) || '[]');
        arr.unshift(Object.assign({saved_at: new Date().toISOString()}, payload));
        localStorage.setItem(key, JSON.stringify(arr));
        showModal('Inquiry saved (demo)','Saved locally in your browser storage. Mail client will open next.');
      }catch(e){ console.error(e); showModal('Save error','Could not save locally'); }
      setTimeout(()=>{ window.location.href = 'mailto:hello@click2hedge.example?subject='+subject+'&body='+body; },800);
    }
  });
}

document.querySelectorAll('form#contactForm').forEach(f=>handleContactForm(f));

// Initialize OTP controls for phone and email fields in forms
document.querySelectorAll('form#contactForm').forEach(setupOtpControls);

function setupOtpControls(form){
  // attach storage
  if(!form._otpData) form._otpData = {phone:{}, email:{}};

  // helper to create OTP UI for a field
  function createFor(fieldName){
    const field = form.querySelector(`[name="${fieldName}"]`);
    if(!field) return;
    const wrapper = document.createElement('div'); wrapper.className='otp-controls';
    const sendBtn = document.createElement('button'); sendBtn.type='button'; sendBtn.textContent='Send OTP';
    const otpInput = document.createElement('input'); otpInput.className='otp-input'; otpInput.placeholder='Enter OTP'; otpInput.type='text'; otpInput.style.display='none';
    const verifyBtn = document.createElement('button'); verifyBtn.type='button'; verifyBtn.textContent='Verify'; verifyBtn.style.display='none';
    const status = document.createElement('span'); status.className='otp-status'; status.textContent='Not verified';
    wrapper.appendChild(sendBtn); wrapper.appendChild(otpInput); wrapper.appendChild(verifyBtn); wrapper.appendChild(status);
    field.parentNode.appendChild(wrapper);

    sendBtn.addEventListener('click', ()=>{
      const val = field.value.trim();
      if(!val){ showError(field,'Enter value before sending OTP'); return; }
      clearErrors(form);
      // simple phone validation for phone field
      if(fieldName==='phone' && !/^\d{10}$/.test(val)){ showError(field,'Phone must be 10 digits'); return; }
      if(fieldName==='email' && !validateEmail(val)){ showError(field,'Enter a valid email'); return; }
      // generate otp (demo)
      const code = generateOtp();
      form._otpData[fieldName] = {code, expires: Date.now()+5*60*1000, verified:false};
      console.log('Demo OTP for', fieldName, val, code);
      showModal('OTP Sent','Demo OTP: '+code+' (expires in 5 minutes)');
      // show input & verify
      otpInput.style.display='inline-block'; verifyBtn.style.display='inline-block';
      status.textContent='OTP sent';
      // disable send for 30s
      sendBtn.disabled=true; let sec=30; const orig=sendBtn.textContent; const ti=setInterval(()=>{
        sec--; sendBtn.textContent=`Resend (${sec}s)`;
        if(sec<=0){ clearInterval(ti); sendBtn.disabled=false; sendBtn.textContent=orig; }
      },1000);
    });

    verifyBtn.addEventListener('click', ()=>{
      const entered = otpInput.value.trim();
      const data = form._otpData[fieldName];
      if(!data || !data.code){ showModal('No OTP','Please request an OTP first'); return; }
      if(Date.now()>data.expires){ showModal('OTP Expired','Please request a new OTP'); return; }
      if(entered===String(data.code)){
        data.verified = true; status.textContent='Verified'; otpInput.style.display='none'; verifyBtn.style.display='none';
        showModal('Verified','The '+fieldName+' has been verified.');
      } else {
        showModal('Incorrect OTP','The code you entered is incorrect.');
      }
    });
  }

  createFor('phone');
  createFor('email');
}

function generateOtp(){
  return Math.floor(100000 + Math.random()*900000); // 6-digit
}

function validateEmail(email){
  // simple RFC-like check
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showError(el, msg){
  el.classList.add('input-error');
  let sibling = el.parentNode.querySelector('.error-message');
  if(!sibling){
    sibling = document.createElement('div');
    sibling.className = 'error-message';
    el.parentNode.appendChild(sibling);
  }
  sibling.textContent = msg;
}

function clearErrors(form){
  form.querySelectorAll('.error-message').forEach(n=>n.remove());
  form.querySelectorAll('.input-error').forEach(i=>i.classList.remove('input-error'));
}

function showModal(title, text){
  // remove existing
  document.querySelectorAll('.modal-overlay').forEach(n=>n.remove());
  const overlay = document.createElement('div'); overlay.className='modal-overlay';
  const modal = document.createElement('div'); modal.className='modal';
  const h = document.createElement('h3'); h.textContent=title;
  const p = document.createElement('p'); p.textContent = text;
  const btn = document.createElement('button'); btn.className='close'; btn.innerHTML='✕';
  btn.addEventListener('click', ()=>overlay.remove());
  modal.appendChild(btn);
  modal.appendChild(h);
  modal.appendChild(p);
  const ok = document.createElement('button'); ok.className='btn-primary modal-ok'; ok.textContent='OK';
  ok.style.marginTop = '12px';
  ok.addEventListener('click', ()=>overlay.remove());
  modal.appendChild(ok);
  overlay.appendChild(modal);
  document.body.appendChild(overlay);
  // focus OK button for keyboard users
  try{ ok.focus(); }catch(e){}
}

// smooth scroll for internal links
document.querySelectorAll('a[href^="#"]').forEach(a=>{
  a.addEventListener('click', e=>{
    const href=a.getAttribute('href');
    if(href.length>1){
      e.preventDefault();
      document.querySelector(href)?.scrollIntoView({behavior:'smooth'});
    }
  });
});
