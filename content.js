let lastEmailHash = null;

function scanEmail() {

    // Gmail email ID from URL
    const emailHash = window.location.hash;

    // stop if same email
    if (emailHash === lastEmailHash) {
        return;
    }

    const emailElement = document.querySelector(".a3s");
    if (!emailElement) return;

    const emailText = emailElement.innerText;

    if (!emailText || emailText.length < 20) return;

    // mark as scanned
    lastEmailHash = emailHash;

    fetch("http://127.0.0.1:5000/api/check_email", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({email_text: emailText})
    })
    .then(res => res.json())
    .then(data => {

        let popup = document.getElementById("phish-popup");

        if (!popup) {
            popup = document.createElement("div");
            popup.id = "phish-popup";
            popup.style.position = "fixed";
            popup.style.bottom = "20px";
            popup.style.right = "20px";
            popup.style.backgroundColor = "#222";
            popup.style.color = "#fff";
            popup.style.padding = "15px";
            popup.style.borderRadius = "8px";
            popup.style.zIndex = "9999";
            popup.style.boxShadow = "0 0 10px #000";
            document.body.appendChild(popup);
        }

        popup.innerHTML = `<b>${data.prediction}</b><br>Confidence: ${data.spam_probability}%`;

    })
    .catch(err => console.log(err));
}

// run checker
setInterval(scanEmail, 1500);