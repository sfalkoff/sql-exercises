#!/bin/env python

"""An interactive, REPL-style quizzer for SQL problems."""

import os
import pickle
import sqlite3
import hashlib
import logging

log = logging.getLogger(__name__)

PROBLEM_FILE_PATH = "problem_set.pickle"
INTRO = """

Hackbright Academy - Introductory SQL Exercise
----------------------------------------------

You will write a series of SQL queries accomplishing different tasks.
Each problem will include a link to a SQLZoo tutorial that illustrates
the concepts required, as well as a link to syntax reference for the
kind of query you'll be doing.

Type '.help' without quotes for a list of the available commands.

It will be helpful to refer to the list of tables, found by typing in '.tables',
or viewing the schema of a given table, (ex: .schema orders) while formulating
your queries. If you get very stuck each problem includes a hint on how to
formulate your query, accessed by typing '.hint'.

"""

HELP = """
The following commands are available:

    .help    - Display this message
    .hint    - Show a hint about how to formulate the query
    .next    - Skip the current problem
    .problem - Show the current problem statement
    .quit    - Quit the program
    .schema <table_name> - Show the schema used to define a given table
    .tables  - Show all the tables available in the database

Any other commands will be interpreted as a SQL query and executed against the
problem set database."""


class Problem(object):
    """SQL Problem."""

    def __init__(self, num, instruction, task, hint, solution):
        self.num = num
        self.instruction = instruction
        self.task = task
        self.hint = hint
        self.solution = solution
        self.solution_hash = None

    def check_solution(self, result_str):
        """Check if result (as string table) matches hashed solution."""

        digest = hashlib.md5(result_str).hexdigest()
        return self.solution_hash == digest

    def hash_solution(self, result_str):
        """Return hash of solution to store."""

        return hashlib.md5(result_str).hexdigest()


class StudentAnswer(object):
    """Correct answer from student."""

    PARTS_SPLIT = "\n\n-----\n\n"

    def __init__(self, num, task, solution):
        self.num = num
        self.task = task
        self.solution = solution

    @classmethod
    def from_string(cls, s):
        """Create student answer from string."""

        num, task, solution = s.split(cls.PARTS_SPLIT)
        return StudentAnswer(num=int(num), task=task, solution=solution)

    def to_string(self):
        """Marshall student answer as string."""

        return self.PARTS_SPLIT.join([str(self.num), self.task, self.solution])


class StudentProgress(dict):
    """Track student progress and handle reading/writing answer file.

    Is a dictionary of answers given by students, along with methods for
    reading and writing out to disk.
    """

    ANSWER_FILE_PATH = 'answers.sql'
    PROBLEM_SPLIT = "\n\n\n==========\n"
    
    def __init__(self):
        super(StudentProgress, self).__init__(self)
        self.read_answers()

    def read_answers(self):
        """Read student answers from file."""

        if not os.path.isfile(self.ANSWER_FILE_PATH):
            return

        with open(self.ANSWER_FILE_PATH, 'r') as f:
            for problem in f.read().split(self.PROBLEM_SPLIT):
                if not problem: 
                    continue
                answer = StudentAnswer.from_string(problem)
                self[answer.num] = answer

        log.info("Read %s answers", len(self))

    def save_answers(self):
        """Save student answers to a file."""

        with open(self.ANSWER_FILE_PATH, 'w') as f:
            f.write(self.PROBLEM_SPLIT.join(
                v.to_string() for k, v in sorted(self.items())))

        log.info("Saved %s answers", len(self))

    def mark_solved(self, num, task, solution):
        """Note that a problem has been solved and save it."""

        self[num] = StudentAnswer(num, task, solution)
        self.save_answers()


class Database(object):
    """Database proxy.

    Handles connecting, executing functions, and DB utilities.
    """

    def __init__(self):
        self.cursor = self.connect()

    def connect(self):
        """Connect to DB and return cursor."""

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.arraysize = 20   # Only read results of up to 20 rows
        return cursor

    @staticmethod
    def _result_to_str(results):
        """Results as string in |-joined table format, like SQLite does."""

        return "\n".join("|".join([str(col) for col in row]) for row in results)

    def get_result(self, attempt):
        """Execute SQL string and return string table of results."""

        try:
            self.cursor.execute(attempt)
            results = self.cursor.fetchmany()
        except sqlite3.OperationalError as e:
            print "There was a problem with your SQL syntax:\n\n\t%s\n" % e
            return

        return self._result_to_str(results)

    def show_tables(self):
        """Show tables."""

        query = "SELECT NAME FROM Sqlite_Master WHERE type='table';"
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        print "Tables:\n", self._result_to_str(results)

    def show_schema(self, tokens):
        """Show schema for given table."""

        if len(tokens) < 2:
            print "Please indicate a table name, like '.schema melons'"
            return

        table_name = tokens[1]
        query = "SELECT sql FROM Sqlite_Master WHERE type='table' AND name=?""";
        self.cursor.execute(query, (table_name,))
        results = self.cursor.fetchall()

        output = self._result_to_str(results)
        if not output:
            print "No such table:", table_name
        else:
            print output


class SQLQuiz(object):
    """Quiz application object.

    Handles state of play and is controller for application.
    """

    def __init__(self):
        self.db = Database()
        self.problems = self.read_problems()
        self.progress = StudentProgress()

    def read_problems(self):
        """Read problems off disk."""

        with open(PROBLEM_FILE_PATH) as f:
            return pickle.load(f)

    def play(self):
        """Play quiz."""

        if len(self.progress) == len(self.problems):
            return self.exit("You've already answered all the questions." +
              "Remove answers.sql to redo the exercise.")

        print INTRO

        for problem in self.problems:
            self.current_problem = problem

            if problem.num in self.progress:
                print "Already answered question %s" % problem.num

            else:
                self.show_problem()
                if not self.get_solution():
                    # True is problem skipped/solved
                    # False is request to quit program.
                    self.exit("Quitting.")

    def exit(self, msg):
        """Hard exit with message."""

        print msg, "\nGoodbye.\n"
        sys.exit(0)

    def show_problem(self):
        """Show problem description and task."""

        print "\nProblem %2.0f" % self.current_problem.num
        print   "----------\n"
        print self.current_problem.instruction
        print
        print "Task:", self.current_problem.task

    def get_solution(self):
        """Get input from user until they quit or are correct."""

        problem = self.current_problem

        while True:
            try:
                print
                line = raw_input("SQL [%d]> " % problem.num)
            except EOFError:
                return False

            if not line:
                continue

            tokens = line.split()
            command = tokens[0].lstrip(".")

            if command in ["q", "exit", "quit"]:
                return False

            elif command in ["problem", "p"]:
                self.show_problem()

            elif command in ["hint"]:
                print problem.hint

            elif command in ["tables", "table"]:
                self.db.show_tables()

            elif command in ["schema"]:
                self.db.show_schema(tokens)

            elif command in ["help", "h", "?"]:
                print HELP

            elif command in ["next", "skip"]:
                print "Skipping problem %d" % problem.num
                return True

            else:
                result = self.db.get_result(line)
                if result:
                    print result
                    if problem.check_solution(result) is True:
                        print "\n\tCorrect!"
                        print "\t", line
                        print "\tMoving on...\n"
                        self.progress.mark_solved(problem.num, problem.task, line)
                        return True


def write_pickle():
    """Write out problems file.

    This is only used by instructors, and requires you have the Python module
    called problems.
    """

    from problems import PROBLEMS

    db = Database()

    problems = []
    for i, p in enumerate(PROBLEMS):
        problem = Problem(num=i + 1, **p)
        problem.solution_hash = problem.hash_solution(
            db.get_result(problem.solution))
        problem.solution = None
        problems.append(problem)

    with open(PROBLEM_FILE_PATH, 'w') as f:
        pickle.dump(problems, f)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2 and sys.argv[1] == "--rebuild":
        write_pickle()
    else:
        quiz = SQLQuiz()
        quiz.play()