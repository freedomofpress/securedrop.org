import zxcvbn from 'zxcvbn'

document.addEventListener('DOMContentLoaded', () => {
	const input = document.getElementById('id_password1')
	if (input) {
		const scoreBar = document.createElement('div')
		scoreBar.className = 'password-score'
		input.parentElement.appendChild(scoreBar)

		const scoreBarChildren = []
		for (let i=0; i < 5; i++) {
			const child = document.createElement('div')
			scoreBar.appendChild(child)
			scoreBarChildren.push(child)
		}

		const calculateScore = () => {
			const email = document.getElementById('id_email')
			const username = document.getElementById('id_username')
			const first_name = document.getElementById('id_first_name')
			const last_name = document.getElementById('id_last_name')

			const user_inputs = []
			if (email) user_inputs.push(email.value)
			if (username) user_inputs.push(username.value)
			if (first_name) user_inputs.push(first_name.value)
			if (last_name) user_inputs.push(last_name.value)

			const result = zxcvbn(input.value.slice(0, 100), user_inputs)

			scoreBarChildren.forEach((child, index) => {
				if (index <= result.score) {
					child.className = `password-score__box password-score__score${result.score}`
				} else {
					child.className = `password-score__box password-score__empty`
				}
			})
		}

		input.addEventListener('keyup', calculateScore)
		input.addEventListener('change', calculateScore)
		calculateScore()
	}
})
