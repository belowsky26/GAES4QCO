# FONT-CODE: tests/step_size/test_step_size_model.py

import pytest
from uuid import UUID

# Importando a classe que vamos testar
from src1.GAES4QCO.step_size.step_size_model import StepSize

# Usamos a convenção "Arrange, Act, Assert" para estruturar os testes.

def test_step_size_initialization_is_correct():
    """
    Testa se os valores iniciais de um StepSize são definidos corretamente.
    """
    # --- ARRANGE (Arrumar o cenário) ---
    variation = 0.1
    c = 0.85
    history_len = 10

    # --- ACT (Agir - executar a lógica) ---
    step_size = StepSize(variation=variation, c=c, history_len=history_len)

    # --- ASSERT (Verificar o resultado) ---
    assert isinstance(step_size.id, UUID)
    assert step_size.variation == variation
    assert step_size.c == c
    assert step_size.history_len == history_len
    assert len(step_size.history) == 0
    assert step_size.history.maxlen == history_len


def test_add_hit_updates_history():
    """
    Testa se o método add_hit adiciona corretamente ao histórico.
    """
    # --- ARRANGE ---
    step_size = StepSize(variation=0.1, c=0.85, history_len=5)

    # --- ACT ---
    step_size.add_hit(True)
    step_size.add_hit(False)
    step_size.add_hit(True)

    # --- ASSERT ---
    assert list(step_size.history) == [1, 0, 1]
    assert len(step_size.history) == 3


def test_reset_variation_decreases_on_high_success():
    """
    Testa se a variação diminui quando a taxa de sucesso é alta.
    (A regra é: sucesso > 1/5, ou seja, mais de 20%)
    """
    # --- ARRANGE ---
    step_size = StepSize(variation=0.1, c=0.5, history_len=5)
    # Forçamos um histórico com alta taxa de sucesso (40%)
    step_size.history.extend([1, 0, 1, 0, 0])

    # --- ACT ---
    # Chamamos o add_hit que internamente chama __reset_variation
    step_size.add_hit(True) # Agora o histórico tem 3 sucessos em 5 (60%)

    # --- ASSERT ---
    # A variação inicial (0.1) deve ser dividida por c (0.5)
    assert step_size.variation == pytest.approx(0.2)


def test_reset_variation_increases_on_low_success():
    """
    Testa se a variação aumenta quando a taxa de sucesso é baixa.
    """
    # --- ARRANGE ---
    step_size = StepSize(variation=0.1, c=0.5, history_len=5)
    # Forçamos um histórico com baixa taxa de sucesso (0%)
    step_size.history.extend([0, 0, 0, 0])

    # --- ACT ---
    step_size.add_hit(False) # Agora o histórico tem 0 sucessos em 5 (0%)

    # --- ASSERT ---
    # A variação inicial (0.1) deve ser multiplicada por c (0.5)
    assert step_size.variation == pytest.approx(0.05)