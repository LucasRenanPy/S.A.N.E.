document.addEventListener("DOMContentLoaded", function () {
  const formSignin = document.querySelector('#signin');
  const formSignup = document.querySelector('#signup');
  const btnColor = document.querySelector('.btnColor');
  const btnSignin = document.querySelector('#btnSignin');
  const btnSignup = document.querySelector('#btnSignup');
  const container = document.querySelector('.container');

  function ajustarAltura(form) {
    if (container && form) {
      container.style.height = form.scrollHeight + 100 + "px";
    }
  }

  if (formSignin && formSignup && btnColor && btnSignin && btnSignup) {
    btnSignin.addEventListener('click', () => {
      formSignin.style.left = "25px";
      formSignup.style.left = "450px";
      btnColor.style.left = "0px";
      ajustarAltura(formSignin);

      btnSignin.classList.add("active");
      btnSignup.classList.remove("active");
    });

    btnSignup.addEventListener('click', () => {
      formSignin.style.left = "-450px";
      formSignup.style.left = "25px";
      btnColor.style.left = "110px";
      ajustarAltura(formSignup);

      btnSignup.classList.add("active");
      btnSignin.classList.remove("active");
    });

    // inicia com Login ativo
    btnSignin.classList.add("active");
    ajustarAltura(formSignin);
  } else {
    console.warn("Alguns elementos não foram encontrados no DOM.");
  }
});
