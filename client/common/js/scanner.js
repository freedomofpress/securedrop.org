document.addEventListener('DOMContentLoaded', () => {
  const submit = document.getElementById('js-submit-button')
  if(submit) {
    submit.addEventListener('click', (event)=> {
      const form = document.getElementById('js-scanner-form')
      const spinner = document.getElementById('js-spinner')
      form.classList.add('basic-form--hidden')
      spinner.classList.remove('spinner--hidden')
    })
  }
})
