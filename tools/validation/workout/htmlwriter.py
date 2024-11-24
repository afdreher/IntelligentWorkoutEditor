import datetime

from .steps import AbstractWorkoutStep, CoolDownWorkoutStep, RecoverWorkoutStep, RepetitionStep, RestWorkoutStep, RunWorkoutStep, WarmUpWorkoutStep
from .workout import Workout
from .goals import AbstractWorkoutStepGoal, CadenceGoal, HeartRateGoal, HeartRateZoneGoal, LapTimeGoal, PowerGoal, SpeedGoal
from .object import WorkoutObject
from .steps.abstract import OptionalGoals

class HTMLWriter(object):

    def to_html(self, item: WorkoutObject, level: int = 0) -> str:
        if isinstance(item, Workout):
            return self._workout_to_html(item)
        elif isinstance(item, AbstractWorkoutStep):
            return self._workout_step_to_html(item, level)
        return ""

    def _workout_to_html(self, workout: Workout) -> str:
        """Convert the Workout Object to basic HTML"""
        result = '<div class="workout"><div class="header"><div class="name"><span class="label">Name:&nbsp;</span>'

        if workout.name is None:
            result += f'<span class="value unnamed">Unnamed workout</span>'
        else:
            result += f'<span class="value named">{workout.name}</span>'
        result += '</div></div><ol>'

        level = 1
        for step in workout.steps:
             result += f'<li>{self.to_html(step, level)}</li>'

        result += '</ol>'
        result += self._notes_to_html(workout.notes)
        result += '</div>'
        return result
    
    @property
    def _color_bar(self) -> str:
        return '<div class="color-bar"></div>'
    
    def _badge(self, step_type: str) -> str:
        return f'<div class="badge"><span>{step_type}</span></div>'
    
    def _step_range_with_unit(self, step: AbstractWorkoutStep, unit: str) -> str:
        return_string = ''
        if step.minimum is not None:
            if step.maximum is not None:
                return_string = f'{step.minimum} to {step.maximum} {unit}'
            else:
                return_string = f'&gt; {step.minimum} {unit}'
        elif step.maximum is not None:
                return_string = f'&lt; {step.maximum} {unit}'

        if step.value is not None:
            target_string = f'{step.value} {unit}'
            if len(return_string) > 0:
                return_string += f'; target: {target_string}'
            else:
                return_string = target_string

        return return_string
    
    def _step_time(self, step: AbstractWorkoutStep) -> str:
        return_string = ''
        if step.minimum is not None:
            min_time = str(datetime.timedelta(seconds=step.minimum))
            if step.maximum is not None:
                return_string = f'{min_time} to {str(datetime.timedelta(seconds=step.maximum))}'
            else:
                return_string = f'&gt; {min_time}'
        elif step.maximum is not None:
                return_string = f'&lt; {str(datetime.timedelta(seconds=step.maximum))}'

        if step.value is not None:
            target_time = str(datetime.timedelta(seconds=step.value))
            if len(return_string) > 0:
                return_string += f'; target: {target_time}'
            else:
                return_string = target_time

        return return_string

    def _workout_step_to_html(self, step: AbstractWorkoutStep, level: int = 0) -> str:
        """Convert the Workout Step to basic HTML"""

        if isinstance(step, RepetitionStep):
            return self._repetition_step_to_html(step, level)
    
        step_type = 'unknown'
        if isinstance(step, CoolDownWorkoutStep):
            step_type = 'cool-down'
        elif isinstance(step, RecoverWorkoutStep):
            step_type = 'recover'
        elif isinstance(step, RestWorkoutStep):
            step_type = 'rest'
        elif isinstance(step, RunWorkoutStep):
            step_type = 'run'
        elif isinstance(step, WarmUpWorkoutStep):
            step_type = 'warm-up'

        result = f'<div class="step {step_type} level_{level}">{self._color_bar}{self._badge(step_type)}<div class="details">'

        result += '<div class="value"><span class="label">Duration:&nbsp;</span><span class="text">'
        if step.unit is None or step.minimum is None and step.maximum is None and step.value is None:
            result += 'Button Press'
        if step.unit == 'seconds':
            # Convert to time...
            result += self._step_time(step)
        else:
            result += self._step_range_with_unit(step, step.unit)
        result += '</span></div>'
        result += self._notes_to_html(step.notes)
        result += '</div></div>'

        return result

    def _repetition_step_to_html(self, repetition: RepetitionStep, level: int = 0) -> str:
        """Convert the Repetition Step to basic HTML"""
        
        result = f'<div class="step repetition level_{level}">{self._badge("repetition")}{self._color_bar}<div class="details">'
        result += f'<div class="value"><span class="label">{self._step_range_with_unit(repetition, "times")}</span></div>'
        result += ' <div class="steps"><ol>'
        level += 1
        for step in repetition.steps:
             result += f'<li>{self.to_html(step, level)}</li>'

        result += '</ol></div>'
        result += self._notes_to_html(repetition.notes)
        result += '</div>'

        result += '</div>'

        return result
    
    def _notes_to_html(self, notes: str | None) -> str:
        if notes is None:
            return ''
        
        #'.notes > .label::before {content: "\01F4D3";}'
        return f'<div class="notes"><span class="label">&#x1F4D3;</span><span class="text">{notes}</span></div>'
    
    def _bounds_to_html(self, obj) -> str:
        result = ''
        if obj is None:
            return ''
        
        if obj.minimum is not None:
            result += f'<span class="minimum">{obj.minimum}</span>'
        if obj.value is not None:
            result += f'<span class="value">{obj.minimum}</span>'
        if obj.maximum is not None:
            result += f'<span class="maximum">{obj.maximum}</span>'
        return result

    def _goals_to_html(self, goals: OptionalGoals) -> str:
        if goals is None:
            return ''
        
        result = '<ul>'
        if goals.cadence is not None:
            result += f'<li><span class="cadence">{self._bounds_to_html(goals.cadence)}<span></li>'
        if goals.heart_rate is not None:
            result += f'<li><span class="heart_rate">{self._bounds_to_html(goals.heart_rate)}<span></li>'
        if goals.heart_rate_zone is not None:
            result += f'<li><span class="heart-rate-zone">{self._bounds_to_html(goals.heart_rate_zone)}<span></li>'
        if goals.lap_time is not None:
            result += f'<li><span class="lap-time">{self._bounds_to_html(goals.lap_time)}<span></li>'
        if goals.power is not None:
            result += f'<li><span class="power">{self._bounds_to_html(goals.power)}<span></li>'
        if goals.speed is not None:
            result += f'<li><span class="speed">{self._bounds_to_html(goals.speed)}<span></li>'
        result = '</ul>'

        return result