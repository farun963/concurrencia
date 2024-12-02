import threading
import time
import random
import queue
import logging
from dataclasses import dataclass

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s'
)


@dataclass
class Student:
    id: int
    research_topic: str


class TeacherConsultationSystem:
    def __init__(self, max_wait_queue=5):
        self.consultation_queue = queue.Queue(maxsize=max_wait_queue)
        self.teacher_available = threading.Semaphore(1)
        self.student_ready = threading.Semaphore(0)
        self.queue_mutex = threading.Lock()
        self.simulation_complete = threading.Event()

    def student_arrive(self, student):
        """Simula la llegada de un estudiante"""
        try:
            self.consultation_queue.put(student, block=True, timeout=0.5)
            logging.info(f"Estudiante {student.id} entra a la cola de espera")
            self.student_ready.release()
        except queue.Full:
            logging.warning(f"Estudiante {student.id} no pudo entrar - Cola llena")

    def professor_attend(self):
        """Simula la atención del profesor"""
        while True:
            self.student_ready.acquire()

            # Finalizar si la simulación completó y se colocó un marcador en la cola
            with self.queue_mutex:
                if not self.consultation_queue.empty():
                    student = self.consultation_queue.get()
                    if student is None:  # Marcador de terminación
                        break

                    logging.info(f"Profesor atiende a estudiante {student.id}")
                    time.sleep(random.uniform(0.3, 0.8))  # Consulta rápida
                    logging.info(f"Consulta con estudiante {student.id} finalizada")


def simulate_students(system, num_students):
    """Simula la llegada de estudiantes"""
    for i in range(1, num_students + 1):
        student = Student(id=i, research_topic=f"Tema de Investigación {i}")
        threading.Thread(
            target=system.student_arrive,
            args=(student,),
            name=f"Student-{i}"
        ).start()
        time.sleep(random.uniform(0.05, 0.2))  # Intervalos cortos entre llegadas


def main():
    num_students = 10
    consultation_system = TeacherConsultationSystem()

    professor_thread = threading.Thread(
        target=consultation_system.professor_attend,
        name="Professor"
    )
    professor_thread.start()

    simulate_students(consultation_system, num_students)

    # Esperar unos segundos y terminar la simulación
    time.sleep(5)
    consultation_system.consultation_queue.put(None)  # Marcador de terminación
    consultation_system.student_ready.release()  # Desbloquear al profesor


    professor_thread.join()

    logging.info("Simulación de consultas finalizada")


if __name__ == "__main__":
    main()