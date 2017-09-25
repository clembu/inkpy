class Story():
    def __init__(self, json):
        "Construct a Story object using a JSON string compiled through inklecate."
        self.allowExternalFunctionFallbacks = False

    @property
    def inkVersion(self):
        """The current version of the ink story file format.
        """
        return 17

    @property
    def currentChoices(self):
        """The list of Choice objects available at the current point in
        the Story. This list will be populated as the Story is stepped
        through with the Continue() method. Once canContinue becomes
        false, this list will be populated, and is usually
        (but not always) on the final Continue() step.
        """
        return []

    @property
    def currentText(self):
        """The latest line of text to be generated from a Continue() call.
        """
        return str(self)

    @property
    def currentTags(self):
        """Gets a list of tags as defined with '#' in source that were seen
        during the latest Continue() call.
        """
        return []

    @property
    def currentErrors(self):
        """Any errors generated during evaluation of the Story.
        """
        return []

    @property
    def hasError(self):
        """Whether the currentErrors list contains any errors.
        """
        return False

    @property
    def variablesState(self):
        """The VariablesState object contains all the global variables in the story.
        However, note that there's more to the state of a Story than just the
        global variables. This is a convenience accessor to the full state object.
        """
        return None

    @property
    def state(self):
        """The entire current state of the story including (but not limited to):

         * Global variables
         * Temporary variables
         * Read/visit and turn counts
         * The callstack and evaluation stacks
         * The current threads
        """
        return None

    # TODO: state

    def ToJson(self):
        "The Story itself in JSON representation."
        return str(self)

    def ResetState(self):
        "Reset the Story back to its initial state as it was when it was first constructed."
        pass

    def ResetErrors(self):
        "Reset the runtime error list within the state."
        pass

    def ResetCallstack(self):
        """Unwinds the callstack. Useful to reset the Story's evaluation
        without actually changing any meaningful state, for example if
        you want to exit a section of story prematurely and tell it to
        go elsewhere with a call to ChoosePathString(...).
        Doing so without calling ResetCallstack() could cause unexpected
        issues if, for example, the Story was in a tunnel already.
        """
        pass

    def Continue(self):
        """Continue the story for one line of content, if possible.
        If you're not sure if there's more content available, for example if you
        want to check whether you're at a choice point or at the end of the story,
        you should call `canContinue` before calling this function.
        """
        return str(self)

    def ContinueMaximally(self):
        """Continue the story until the next choice point or until it runs out of content.
        This is as opposed to the Continue() method which only evaluates one line of
        output at a time.
        """
        return str(self)

    @property
    def canContinue(self):
        """Check whether more content is available if you were to call `Continue()` - i.e.
        are we mid story rather than at a choice point or at the end.
        """
        return True

    def ChoosePathString(self, path, *args):
        """Change the current position of the story to the given path.
        From here you can call Continue() to evaluate the next line.
        The path string is a dot-separated path as used internally by the engine.
        These examples should work:

           myKnot
           myKnot.myStitch

        Note however that this won't necessarily work:

            myKnot.myStitch.myLabelledChoice

        ...because of the way that content is nested within a weave structure.
        """
        pass

    def ChooseChoiceIndex(self, idx):
        """Chooses the Choice from the currentChoices list with the given
        index. Internally, this sets the current content path to that
        pointed to by the Choice, ready to continue story evaluation.
        """
        pass

    def HasFunction(self, fname):
        """Checks if a function exists.
        """
        return False

    def EvaluateFunction(self, f, *args):
        """Evaluates a function defined in ink.
        """
        return None

    def BindExternalFunction(self, fname, func):
        """Bind a python function to an ink EXTERNAL function declaration.
        """
        pass

    def UnbindExternalFunction(self, fname):
        """Remove a binding for a named EXTERNAL ink function.
        """
        pass

    def ValidateExternalBindings(self):
        """Check that all EXTERNAL ink functions have a valid bound C# function.
        Note that this is automatically called on the first call to Continue().
        """
        pass

    def ObserveVariables(self, obs, *vnames):
        """When the named global variable changes it's value, the observer will be
        called to notify it of the change. Note that if the value changes multiple
        times within the ink, the observer will only be called once, at the end
        of the ink's evaluation. If, during the evaluation, it changes and then
        changes back again to its original value, it will still be called.
        Note that the observer will also be fired if the value of the variable
        is changed externally to the ink, by directly setting a value in
        story.variablesState.
        """
        pass

    def RemoveVariableObserver(self, obs):
        """Removes the variable observer, to stop getting variable change notifications.
        If you pass a specific variable name, it will stop observing that particular one. If you
        pass null (or leave it blank, since it's optional), then the observer will be removed
        from all variables that it's subscribed to.
        """
        pass

    @property
    def globalTags(self):
        """Get any global tags associated with the story. These are defined as
        hash tags defined at the very top of the story.
        """
        return []

    def TagsForContentAtPath(self, path):
        """Gets any tags associated with a particular knot or knot.stitch.
        These are defined as hash tags defined at the very top of a
        knot or stitch.
        """
        return []

    def BuildStringOfHierarchy(self):
        """Useful when debugging a (very short) story, to visualise the state of the
        story. Add this call as a watch and open the extended text. A left-arrow mark
        will denote the current point of the story.
        It's only recommended that this is used on very short debug stories, since
        it can end up generate a large quantity of text otherwise.
        """
        return str(self)
