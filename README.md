# hansel

*Hansel, he's so hot right now*

Trying to add some simple domain validation without needing to subclass. Ideally the domain model shouldn't include any persistence logic or care whether it's driven by tornado, flask, or a CLI.

We'll see how it goes.

```python
class Question(Entity):
    id = UUID()
    text = Unicode()
    hint = Unicode()
    options = List('QuestionOption')

class QuestionService(Service):
  with Service.UL():
    question_id = UUID()
    option_id = UUID()
    created = Datetime()

  def foo(self, question_id, option_id, created):
    ...
```

The basic model validation is straight forward. What I'm wanting now is to automatically validate function arguments based on some ubiquitous language(UL). Within a service class it seems reasonable that certain variable names will always be a certain type. Right now this is attached to a concrete service class. Might be worthwhile to attach it to a bounded context and then have the service validate off of the BC.

Also feasible to validate all variable names within a BC and not just parameters.

Something I also want is to be able to reference `Question.id` and validate not just the type, but also whether a `UUID` for a `Question` entity. This would be more applicable within the domain model and not the boundary since at the application layer we'd just have to assume a valid `UUID` until get verify against some store. I'd rather not have to create a `UUID` subclass like `QuestionId(UUID)`.
