from block_app.services.password_service import password_hashing, password_strength
import bcrypt


class TestPasswordSecurity:
    # Testing Password Hashing
    def test_hashing(self):
        password = 'my_password'
        returned_password = password_hashing(password)
        hash = bcrypt.hashpw(password.encode(), returned_password['salt'])
        assert returned_password['hash'] == hash

    # Testing Password Strength Score
    def test_strength(self):
        password_0 = ''
        password_1 = 'mypassword'
        password_2 = 'MYPASSWORD'
        password_3 = 'Mypassword'
        password_4 = 'Myp@ssword'
        password_5 = 'Myp@ssw0rd'


        returned_score_0 = password_strength(password_0)
        print(f'Returned score 1: {returned_score_0}')

        returned_score_1 = password_strength(password_1)
        print(f'Returned score 1: {returned_score_1}')

        returned_score_2 = password_strength(password_2)
        print(f'Returned score 2: {returned_score_2}')

        returned_score_3 = password_strength(password_3)
        print(f'Returned score 3: {returned_score_3}')

        returned_score_4 = password_strength(password_4)
        print(f'Returned score 4: {returned_score_4}')

        returned_score_5 = password_strength(password_5)
        print(f'Returned score 5: {returned_score_5}')

        assert returned_score_0 == 0

        assert not returned_score_1 == 1
        assert returned_score_1 == 2

        assert returned_score_2 == 2
        assert returned_score_3 == 3
        assert returned_score_4 == 4
        assert returned_score_5 == 5

