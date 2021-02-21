document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';

  // Submit a POST request to send an email
  document.querySelector('#compose-form').onsubmit = () => {
    fetch('/emails', {
      method:'POST',
      body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
      })
    })
    .then(response => response.json())
    .then(() => {
      load_mailbox('sent');
    });
    return false;
  };
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#read-email').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
  // GET all the mails in mailbox
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      for (let email of emails) {
        if (email.archived && mailbox == 'inbox') {
          continue;
        }
        const emailDiv = document.createElement('div');
        emailDiv.setAttribute("class", `email-box`);
        email.read ? emailDiv.style.backgroundColor = 'gainsboro' : emailDiv.style.backgroundColor = 'white';
        if (mailbox == 'sent'){
          emailDiv.innerHTML = `
          <div class="p-2" style="font-weight: bold;">To: ${email.recipients}</div>
          <div class="p-2">${email.subject}</div>
          <div class="ml-auto p-2">${email.timestamp}</div>
          `;
        } else {
        emailDiv.innerHTML = `
          <div class="p-2" style="font-weight: bold;">${email.sender}</div>
          <div class="p-2">${email.subject}</div>
          <div class="ml-auto p-2">${email.timestamp}</div>
        `;
        }

        //Append the emailDiv to overall list of email boxes displayed in mailbox
        document.querySelector('#emails-view').appendChild(emailDiv);

        emailDiv.addEventListener('click', () => load_email(email));
      }
    });

}

function load_email(email) {
  // Show the read-email block and hide the other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#read-email').style.display = 'block';

  // mark email as read
  fetch('/emails/'+`${email.id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  });

  fetch(`/emails/${email.id}`)
  .then(response => response.json())
  .then(email => {
    document.querySelector('#read-email').innerHTML = `<h4>${email.subject}</h4>`;
    const emailDiv = document.createElement('div');
    emailDiv.setAttribute("class", `email-container`);
    emailDiv.innerHTML = `
      <span style="font-weight: bold">From: </span>${email.sender}<br>
      <span style="font-weight: bold">To: </span>${email.recipients}<br>
      <span style="font-weight: bold">Timestamp: </span>${email.timestamp}<br>
      <hr>
      ${email.body}
      <hr>
      <div>
        <button class="btn btn-primary btn-sm" id="reply">Reply</button>
        <button class="btn btn-primary btn-sm" id="archive">${email.archived ? "Unarchive" : "Archive"}</button>
      </div>
      
    `;
    document.querySelector('#read-email').append(emailDiv);

    document.querySelector('#reply').addEventListener('click', () => {
      compose_email();
      if (email.subject.slice(0,4) != "Re: "){
        email.subject = `Re: ${email.subject}`;
      }

      email.body = `"\nOn ${email.timestamp} ${email.sender} wrote: \n${email.body}\n\n"`;

      //prefill the form (for replying)
      document.querySelector('#compose-recipients').value = email.sender;
      document.querySelector('#compose-subject').value = email.subject;
      document.querySelector('#compose-body').value = email.body;
    });

    document.querySelector('#archive').addEventListener('click', () =>{
      fetch(`/emails/${email.id}`, {
        method: 'PUT', 
        body: JSON.stringify({
          archived: !email.archived
        })
      })
      .then(() => load_mailbox("inbox"));
    });
  })




}

